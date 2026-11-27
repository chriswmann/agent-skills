---
name: flow
description: Which skill fits now? A map of the skills in this collection and the order to use them.
disable-model-invocation: true
---

# Flow

Answer the user's question about which skill or sequence fits their situation. Before saying what
a skill does, read its `SKILL.md`; the summaries below are for orientation only.

## Main flow: idea to merged change

1. **`/grill-docs`**: interview until every branch of the plan is resolved, keeping `GLOSSARY.md`
   and ADRs up to date through `domain-model`. Outside a repository, or when no files should be
   written, use **`grill`** instead.
2. **`prototype`**, if a question needs running code to settle. Fold the answer back into the
   conversation.
3. Multi-session work: **`/to-spec`**, then **`/to-tickets`**, then **`/implement`** once per ticket
   in a fresh session, blockers first. Single-session work: **`/implement`** straight from the
   conversation.
4. `/implement` drives **`tdd`** and finishes with **`review-change`** (Standards and Spec axes) and a
   commit. **`pr`** shapes the pull request description.
5. **`/explain-diff`** turns the finished change into a page with a quiz, so the reviewer
   understands it before approving.
6. **`/retro`** after the build, especially one that went badly: it improves the environment for
   next time.

Keep steps 1 to 3 in one context window so the spec and tickets build on the interview. Each
`/implement` starts fresh from its ticket.

## Other entry points

- **Something is broken**: `diagnose`. Afterwards, `/retro` asks what would have prevented it.
- **The codebase is getting hard to change**: `codebase-design` to survey for deepening
  opportunities; take the chosen one into `/grill-docs`.
- **A message did not make sense**: `/wait-what`.
- **Moving to a new session, directory, tool or colleague**: `/handoff`.
- **Claude feels slow or cluttered**: `/setup-audit`, once per profile.
- **Writing or editing a skill or `CLAUDE.md`**: `writing-skills`.

## Between phases

At the end of a phase, choose in this order: **continue** if the next phase needs this context;
**`/clear`** if nothing here matters to what comes next; a **subagent** for a self-contained side
task; **`/handoff`** when the work moves somewhere else; **`/compact`** when the window is getting
full but the work continues here.
