# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Render an explain-diff content spec into one self-contained HTML page.

The page scaffolding, styles and quiz behaviour are the same for every explanation, so they live
here. The agent writes only the content: prose, diagrams and quiz questions.

Usage:
    uv run --script render.py SPEC.json [-o OUTPUT.html]

Without -o, the page is written to the system temporary directory as
YYYY-MM-DD-explanation-<slug>.html, using today's local date. The file is readable only by the
current user. The script prints the path it wrote.

Spec (JSON):
{
  "title": "Retry with backoff in the HTTP client",
  "subtitle": "PR #482",                               (optional)
  "slug": "catalogue-retry-backoff",                   (optional; derived from the title)
  "sections": [
    {"id": "background", "heading": "Background", "html": "<p>...</p>"},
    {"id": "intuition", "heading": "The idea", "html": "<p>...</p>"},
    {"id": "code", "heading": "Code walkthrough", "html": "<pre>...</pre>"}
  ],
  "quiz": [
    {
      "question": "Why does the second request wait longer than the first?",
      "section": "backoff",
      "options": [
        {"text": "The delay doubles after each failure.", "correct": true,
         "why": "`backoff()` multiplies the base delay by 2 for every attempt."},
        {"text": "The server asks for a longer wait each time.", "correct": false,
         "why": "The fetcher ignores `Retry-After`; the delay is computed locally."},
        {"text": "Jitter is added only to later attempts.", "correct": false,
         "why": "Jitter is added to every attempt, including the first."}
      ]
    }
  ]
}

Section "html" is raw HTML and is inserted as written. Section ids must be lower-case letters,
digits and hyphens; "quiz" is reserved. Quiz "question", "text" and "why" are plain text: they
are escaped, and `backticks` become inline code.

Quiz "section" says where the page answers the question. It is a section id, or the id of an
element inside a section's html, such as <h3 id="backoff">. A reader who answers wrongly is shown
a link to it, so point at the narrowest heading that holds the answer.

Quiz rules, checked before anything is written:
  - each question has 3 or 4 options, exactly one of them correct, and every option has a "why";
  - each question has a "section" that names a section id or an id inside a section's html;
  - the correct option may not be more than 20% longer than the longest wrong option;
  - the correct option may not be the longest option in more than half of the questions.
Option order is set by the renderer. The correct answer's position is spread across questions,
and the same spec always renders the same order.

Classes for section HTML:
  <details class="primer"><summary>...</summary>...</details>
                         background a familiar reader can skip
  .callout               key definition, edge case or finding
  .callout.warn          something a reviewer should not miss
  .diagram               framed figure; put a <p class="caption"> inside for a caption
  .flow > .box, .arrow   left-to-right flow of boxes (stacks on narrow screens)
  .box.new / .box.gone / .box.fail
                         added, removed or failing component
  .cols                  two or three side-by-side panels, e.g. before and after
  .mock                  simplified sketch of a screen the user sees
  .badge.new / .badge.gone
                         small inline label
  <pre>                  code; long lines wrap
  <table>                comparison tables
Inline <svg> and the page's own <script> for an interactive figure are allowed.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import html
import json
import os
import random
import re
import sys
import tempfile
from pathlib import Path

SECTION_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ELEMENT_ID = re.compile(r'<[a-zA-Z][^>]*?\bid=["\']([^"\']+)["\']')
TAG = re.compile(r"<[^>]+>")
LENGTH_LEAK_RATIO = 1.2

CSS = """
:root {
  color-scheme: light dark;
  --bg: #fafaf7; --fg: #1d1d1b; --muted: #66645f; --accent: #9a4a1c; --border: #dedad2;
  --surface: #ffffff; --surface-2: #f3f0ea; --code-bg: #24272e; --code-fg: #e8e6e3;
  --inline-code: #ece9e2; --callout: #fbf1e6; --warn: #fdeceb; --warn-edge: #b3261e;
  --new: #e3f4e8; --new-edge: #2e7d4f; --gone: #f6e3e3; --gone-edge: #a33b3b;
  --right: #e3f4e8; --right-fg: #1f5c39; --wrong: #f8e5e3; --wrong-fg: #8a2a22;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #17171a; --fg: #e9e7e2; --muted: #a29f98; --accent: #e39a6b; --border: #34343a;
    --surface: #1f1f23; --surface-2: #26262b; --code-bg: #0f1013; --code-fg: #e8e6e3;
    --inline-code: #2c2c32; --callout: #2a221c; --warn: #331d1c; --warn-edge: #e06c62;
    --new: #1b2c22; --new-edge: #5fbf86; --gone: #301e1f; --gone-edge: #d77b7b;
    --right: #1b2c22; --right-fg: #8fd8ab; --wrong: #331d1c; --wrong-fg: #f0a39b;
  }
}
* { box-sizing: border-box; }
body { margin: 0 auto; max-width: 52rem; padding: 2rem 1rem 6rem; background: var(--bg);
  color: var(--fg); font: 17px/1.65 Georgia, 'Iowan Old Style', serif; overflow-wrap: anywhere; }
h1 { font-size: 1.9rem; line-height: 1.25; margin-bottom: .3rem; }
.subtitle { color: var(--muted); margin-top: 0; }
h2 { font-size: 1.4rem; margin-top: 3rem; padding-bottom: .3rem; border-bottom: 2px solid var(--accent); }
h3 { font-size: 1.1rem; margin-top: 2rem; }
a { color: var(--accent); }
code, pre { font-family: ui-monospace, 'SF Mono', Menlo, Consolas, monospace; }
code { background: var(--inline-code); padding: .05rem .3rem; border-radius: 3px; font-size: .88em; }
pre { background: var(--code-bg); color: var(--code-fg); padding: 1rem 1.2rem; border-radius: 8px;
  overflow-x: auto; white-space: pre-wrap; word-break: break-word; font-size: .85rem; line-height: 1.5; }
pre code { background: none; padding: 0; color: inherit; font-size: inherit; }
.toc { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: .8rem 1.4rem; }
.toc ol { margin: .3rem 0; padding-left: 1.2rem; }
details.primer { background: var(--surface-2); border-radius: 8px; padding: .6rem 1.2rem; margin: 1rem 0; }
details.primer > summary { cursor: pointer; font-weight: bold; }
.callout { background: var(--callout); border-left: 4px solid var(--accent); padding: .8rem 1.2rem;
  border-radius: 0 6px 6px 0; margin: 1.2rem 0; }
.callout.warn { background: var(--warn); border-left-color: var(--warn-edge); }
.diagram { background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
  padding: 1.2rem; margin: 1.4rem 0; overflow-x: auto; }
.diagram svg { max-width: 100%; height: auto; }
.caption { color: var(--muted); font-size: .9rem; margin: .8rem 0 0; text-align: center; }
.flow { display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: .6rem; }
.box { border: 2px solid var(--accent); border-radius: 8px; padding: .5rem .9rem; background: var(--surface-2);
  text-align: center; min-width: 7rem; font-size: .92rem; }
.box.new { border-color: var(--new-edge); background: var(--new); }
.box.gone { border-color: var(--gone-edge); background: var(--gone); text-decoration: line-through; }
.box.fail { border-color: var(--warn-edge); background: var(--warn); }
.arrow { color: var(--muted); font-size: 1.3rem; }
.cols { display: grid; grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr)); gap: 1rem; }
.mock { border: 1px solid var(--border); border-radius: 8px; background: var(--surface); padding: .8rem;
  font: 14px/1.4 system-ui, sans-serif; }
.badge { display: inline-block; font: .75rem system-ui, sans-serif; padding: .1rem .5rem; border-radius: 10px; }
.badge.new { background: var(--new); color: var(--new-edge); }
.badge.gone { background: var(--gone); color: var(--gone-edge); }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: .92rem; display: block; overflow-x: auto; }
th, td { border: 1px solid var(--border); padding: .45rem .7rem; text-align: left; vertical-align: top; }
th { background: var(--surface-2); }
.quiz-intro { color: var(--muted); }
.quiz-q { background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
  padding: 1rem 1.3rem; margin: 1.2rem 0; }
.quiz-q > p { font-weight: bold; margin-top: 0; }
.quiz-opt { display: block; width: 100%; text-align: left; margin: .45rem 0 0; padding: .6rem .9rem;
  border: 1px solid var(--border); border-radius: 6px; background: var(--surface); color: var(--fg);
  font: inherit; font-size: .95rem; cursor: pointer; }
.quiz-opt:hover:not(:disabled) { background: var(--surface-2); }
.quiz-opt:disabled { cursor: default; }
.quiz-opt.right { background: var(--right); border-color: var(--right-fg); }
.quiz-opt.wrong { background: var(--wrong); border-color: var(--wrong-fg); }
.why { margin: .3rem 0 0 .9rem; padding: .4rem .8rem; font-size: .9rem; border-left: 3px solid var(--border); }
.why.right { color: var(--right-fg); border-left-color: var(--right-fg); }
.why.wrong { color: var(--wrong-fg); border-left-color: var(--wrong-fg); }
.reread { margin: .8rem 0 0; font-size: .92rem; }
.score { font-weight: bold; }
.quiz-reset { font: inherit; font-size: .9rem; padding: .4rem .9rem; border-radius: 6px;
  border: 1px solid var(--border); background: var(--surface); color: var(--fg); cursor: pointer; }
"""

QUIZ_JS = """
(() => {
  const questions = [...document.querySelectorAll('.quiz-q')];
  const score = document.querySelector('.score');
  const update = () => {
    const done = questions.filter(q => q.dataset.answered);
    const right = done.filter(q => q.dataset.answered === 'right').length;
    score.textContent = done.length === questions.length
      ? `${right} of ${questions.length} correct.` + (right === questions.length ? ' Passed.' : ' Follow the link under each question you missed, then try again.')
      : `${done.length} of ${questions.length} answered.`;
  };
  questions.forEach(q => {
    q.querySelectorAll('.quiz-opt').forEach(opt => {
      opt.addEventListener('click', () => {
        if (q.dataset.answered) return;
        const isRight = opt.dataset.correct === 'true';
        q.dataset.answered = isRight ? 'right' : 'wrong';
        q.querySelectorAll('.quiz-opt').forEach(o => { o.disabled = true; });
        const reveal = (o, cls) => {
          o.classList.add(cls);
          const why = o.nextElementSibling;
          why.classList.add(cls);
          why.hidden = false;
        };
        reveal(opt, isRight ? 'right' : 'wrong');
        if (!isRight) {
          reveal(q.querySelector('.quiz-opt[data-correct="true"]'), 'right');
          q.querySelector('.reread').hidden = false;
        }
        update();
      });
    });
  });
  document.querySelector('.quiz-reset').addEventListener('click', () => {
    questions.forEach(q => {
      delete q.dataset.answered;
      q.querySelectorAll('.quiz-opt').forEach(o => { o.disabled = false; o.classList.remove('right', 'wrong'); });
      q.querySelectorAll('.why').forEach(w => { w.hidden = true; w.classList.remove('right', 'wrong'); });
      q.querySelector('.reread').hidden = true;
    });
    update();
  });
  // A link into a collapsed primer would land on nothing, so open it first.
  document.querySelectorAll('.reread a').forEach(a => {
    a.addEventListener('click', () => {
      const target = document.getElementById(a.getAttribute('href').slice(1));
      for (let d = target && target.closest('details'); d; d = d.parentElement.closest('details')) d.open = true;
    });
  });
  update();
})();
"""


class SpecError(Exception):
    pass


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "change"


def inline(text: str) -> str:
    """Escape plain text and turn `backticks` into inline code."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", html.escape(text))


def anchors(sections: list[dict]) -> dict[str, str]:
    """Every id a quiz question may link to, mapped to the text of its link."""
    found = {}
    for s in sections:
        sid, heading, body = s.get("id"), s.get("heading"), s.get("html")
        if not all(isinstance(v, str) for v in (sid, heading, body)):
            continue
        found[sid] = heading
        for inner in ELEMENT_ID.findall(body):
            sub = re.search(
                rf'<h[3-6]\b[^>]*\bid=["\']{re.escape(inner)}["\'][^>]*>(.*?)</h[3-6]>',
                body,
                re.S,
            )
            label = html.unescape(TAG.sub("", sub.group(1))).strip() if sub else ""
            found.setdefault(inner, f"{heading}: {label}" if label else heading)
    return found


def validate(spec: dict) -> list[str]:
    errors = []
    if not isinstance(spec.get("title"), str) or not spec["title"].strip():
        errors.append('"title" is required.')
    sections = spec.get("sections")
    if not isinstance(sections, list) or not sections:
        errors.append('"sections" must be a non-empty list.')
        sections = []
    seen = set()
    for i, s in enumerate(sections, 1):
        for key in ("id", "heading", "html"):
            if not isinstance(s.get(key), str) or not s[key].strip():
                errors.append(f'section {i}: "{key}" is required.')
        sid = s.get("id", "")
        if isinstance(sid, str) and sid:
            if not SECTION_ID.match(sid) or sid == "quiz":
                errors.append(
                    f'section {i}: id "{sid}" must be lower-case letters, digits and hyphens, and not "quiz".'
                )
            if sid in seen:
                errors.append(f'section {i}: id "{sid}" is used twice.')
            seen.add(sid)

    quiz = spec.get("quiz", [])
    if not isinstance(quiz, list):
        return errors + ['"quiz" must be a list.']
    longest_correct = 0
    known = anchors(sections)
    for i, q in enumerate(quiz, 1):
        if not isinstance(q.get("question"), str) or not q["question"].strip():
            errors.append(f'question {i}: "question" is required.')
        target = q.get("section")
        if not isinstance(target, str) or not target.strip():
            errors.append(
                f'question {i}: "section" is required: the id of the section, or of a heading in one, that answers it.'
            )
        elif target not in known:
            errors.append(
                f'question {i}: "section" is "{target}", which is not a section id or an id in any section\'s html. '
                f"Known ids: {', '.join(sorted(known)) or 'none'}."
            )
        options = q.get("options")
        if not isinstance(options, list) or not 3 <= len(options) <= 4:
            errors.append(f"question {i}: needs 3 or 4 options.")
            continue
        if any(
            not isinstance(o.get("text"), str) or not o["text"].strip() for o in options
        ):
            errors.append(f'question {i}: every option needs "text".')
            continue
        if any(
            not isinstance(o.get("why"), str) or not o["why"].strip() for o in options
        ):
            errors.append(f'question {i}: every option needs a "why" explaining it.')
        correct = [o for o in options if o.get("correct") is True]
        if len(correct) != 1:
            errors.append(
                f'question {i}: exactly one option must have "correct": true (found {len(correct)}).'
            )
            continue
        right_len = len(correct[0]["text"])
        wrong_max = max(len(o["text"]) for o in options if o is not correct[0])
        if right_len > wrong_max * LENGTH_LEAK_RATIO:
            errors.append(
                f"question {i}: the correct option is {right_len} characters against at most {wrong_max} "
                "for the wrong ones, which gives the answer away. Make the options similar in length and detail."
            )
        if right_len > wrong_max:
            longest_correct += 1
    if quiz and longest_correct * 2 > len(quiz):
        errors.append(
            f"the correct option is the longest in {longest_correct} of {len(quiz)} questions, so a reader can "
            "guess by length. Lengthen some wrong options or tighten some correct ones."
        )
    return errors


def order_options(quiz: list[dict], seed: str) -> list[list[dict]]:
    """Place each question's correct option so positions are spread out, deterministically."""
    rng = random.Random(hashlib.sha256(seed.encode()).hexdigest())
    used: dict[int, int] = {}
    ordered = []
    for q in quiz:
        options = q["options"]
        right = next(o for o in options if o["correct"] is True)
        wrong = [o for o in options if o is not right]
        rng.shuffle(wrong)
        fewest = min(used.get(p, 0) for p in range(len(options)))
        position = rng.choice(
            [p for p in range(len(options)) if used.get(p, 0) == fewest]
        )
        used[position] = used.get(position, 0) + 1
        wrong.insert(position, right)
        ordered.append(wrong)
    return ordered


def render(spec: dict) -> str:
    title = spec["title"]
    sections = spec["sections"]
    quiz = spec.get("quiz", [])

    toc = "\n".join(
        f'<li><a href="#{s["id"]}">{html.escape(s["heading"])}</a></li>'
        for s in sections
    )
    if quiz:
        toc += '\n<li><a href="#quiz">Check your understanding</a></li>'
    body = "\n\n".join(
        f'<h2 id="{s["id"]}">{html.escape(s["heading"])}</h2>\n{s["html"]}'
        for s in sections
    )

    quiz_html = script = ""
    if quiz:
        blocks = []
        seed = title + "".join(q["question"] for q in quiz)
        known = anchors(sections)
        for q, options in zip(quiz, order_options(quiz, seed)):
            opts = "\n".join(
                f'<button type="button" class="quiz-opt" data-correct="{str(o["correct"] is True).lower()}">'
                f'{inline(o["text"])}</button>\n<div class="why" hidden>{inline(o["why"])}</div>'
                for o in options
            )
            reread = (
                f'<p class="reread" hidden>Reread <a href="#{html.escape(q["section"])}">'
                f"{html.escape(known[q['section']])}</a>.</p>"
            )
            blocks.append(
                f'<div class="quiz-q">\n<p>{inline(q["question"])}</p>\n{opts}\n{reread}\n</div>'
            )
        quiz_html = (
            '<h2 id="quiz">Check your understanding</h2>\n'
            f'<p class="quiz-intro">{len(quiz)} questions. Answer each one before you approve or ship the change.</p>\n'
            "<noscript><p>The quiz needs JavaScript.</p></noscript>\n"
            + "\n\n".join(blocks)
            + '\n<p><span class="score"></span> <button type="button" class="quiz-reset">Start again</button></p>'
        )
        script = f"<script>{QUIZ_JS}</script>"

    subtitle = spec.get("subtitle")
    subtitle_html = (
        f'<p class="subtitle">{html.escape(subtitle)}</p>' if subtitle else ""
    )
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<h1>{html.escape(title)}</h1>
{subtitle_html}
<nav class="toc"><strong>Contents</strong>
<ol>
{toc}
</ol>
</nav>

{body}

{quiz_html}
{script}
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("spec", type=Path, help="path to the JSON content spec")
    ap.add_argument("-o", "--output", type=Path, help="output HTML path")
    args = ap.parse_args()

    try:
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read spec: {exc}", file=sys.stderr)
        return 2
    if not isinstance(spec, dict):
        print("spec must be a JSON object", file=sys.stderr)
        return 2
    errors = validate(spec)
    if errors:
        print("Spec problems; fix them and run again:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    out = args.output
    if out is None:
        slug = slugify(spec.get("slug") or spec["title"])
        out = (
            Path(tempfile.gettempdir())
            / f"{datetime.date.today():%Y-%m-%d}-explanation-{slug}.html"
        )
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(render(spec))
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
