---
name: setup-audit
description: Audit one Claude profile for context load and sediment (memory files, skills, MCP servers, settings), then make the changes the user picks.
disable-model-invocation: true
---

# Setup audit

A Claude profile accumulates **sediment**: memory-file lines nobody re-reads, skills installed for
one project, MCP servers tried once. Each piece either costs **context load** on every turn (a
memory line, a model-invoked skill's description, a server's tool list) or adds to the list a
person must keep in their head. This audit measures both and proposes cuts. It is a proposal: the
user picks what happens, and every removal can be undone.

`SKILL_DIR` below is the directory holding this `SKILL.md`. `scripts/scan.py` needs only Python;
run it with `uv run --script`.

## 1. Choose the profile

A profile is a Claude config directory: `~/.claude`, or another used through `CLAUDE_CONFIG_DIR`.
If the user has more than one, ask which to audit, or audit each in turn. Ask also which project
directory they mainly work in, since project skills and memory files live there.

## 2. Measure

```bash
uv run --script "$SKILL_DIR/scripts/scan.py" --profile <profile> --project <dir> --days 30 \
  -o "${TMPDIR:-/tmp}/setup-audit.json"
```

Its `--help` lists exactly what it reads; it writes nothing else. Token figures are characters
divided by four. Where the session offers `/context`, its measured figures replace the estimates.
Usage counts cover transcripts in this profile on this machine only.

## 3. Judge each item

Hold every item to one question: does it change behaviour often enough to pay for its load?

- **Memory files.** Long files are suspect (past roughly 200 lines or 2,500 tokens). Inside them
  look for: rules a linter, type checker or hook could enforce instead; no-ops the model obeys by
  default; pointers to files or commands that no longer exist (check each one); text repeated
  between the profile and project files; step-by-step procedures that would cost nothing as a
  user-invoked skill.
- **Skills.** A model-invoked skill pays for its description every turn. Look for: no recorded use
  in the window; two skills that would fire on the same request (for example the same skill from
  a plugin and a folder); descriptions much over 80 tokens; skills only ever typed by hand, which
  could be user-invoked and cost nothing. Use in other apps or machines does not show up, so ask
  before calling a skill unused.
- **MCP servers.** No recorded calls in the window, or the same server configured at two scopes.
- **Settings.** Permission rules that repeat or contradict each other, `allow` rules wider than
  the work needs, hooks whose script is missing.

## 4. Propose

Write one numbered list, grouped by the four areas and ordered by tokens saved per turn. Each line
gives the item, the evidence (a count, a size, a date), and the proposed change: keep, trim, make
user-invoked, retire, or replace with a check. For more than about twenty lines, offer it as a
private artifact. Ask the user to answer with the numbers they accept, adding a note to any line
where they want something different.

## 5. Change

Carry out the accepted numbers in list order, honouring any note.

**Shared skills.** The scan reports `"symlink": true` for a skill folder that links elsewhere, such
as this repository after `install.sh`. Editing through the link changes the source, and with it
every profile linked to it. Before trimming or changing such a skill, say which profiles share it
and ask: change the shared source, or replace the link in this profile with a local copy and edit
that. Retiring a linked skill moves only the link.

- **Retire** means move, not delete: skill folders go to `<profile>/retired/YYYY-MM-DD/`, and a
  removed MCP server's configuration is copied there first.
- **Trim** and other file edits are shown as a diff and written after the user agrees to that diff.
- **Make user-invoked** adds `disable-model-invocation: true` to the skill's front matter.

On the first failure, stop and report what is done and what remains.

## 6. Report

List each change made, anything skipped and why, where retired items went, and the estimated
tokens saved per turn.
