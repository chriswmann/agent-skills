---
name: grill
description: >
  Interview the user relentlessly about a plan, design or decision until every branch is
  resolved. Use when the user says "grill me" or wants their thinking stress-tested, and as the
  interview step inside other skills.
---

# Grill

Interview the user until you both share one understanding of the plan. Writes no files; for the
version that also keeps `GLOSSARY.md` and ADRs, the user runs `/grill-docs`.

## The design tree

Map the plan as a **design tree**: every decision branches into the decisions that hang off it.
The **frontier** is every open decision whose prerequisites are already settled, the questions you
can ask now without guessing at answers you have not heard.

## Rounds

Ask the whole frontier in one round. Number each question and give your recommended answer, worded
so that "yes" accepts it:

```
**Q1. <short title>.** <question, with the real options if there are any>
→ Recommended: <your answer>

---

**Q2. <short title>.** ...
```

Then wait for the answers. Each answer settles a decision, pushes the frontier outwards and
unblocks the questions that depended on it. Recompute the frontier and ask the next round. A
question that depends on another question still open in this round belongs to a later round.

## Facts and decisions

Finding facts is your job, never the user's. When a frontier question needs a fact from the
environment (the code, the file system, a tool), send a subagent with a fresh context to find it
rather than asking. Do not block on it: only the questions downstream of that lookup wait for it;
ask the rest of the frontier now. Decisions belong to the user: put each one to them and wait.

## Done

The session is done when the frontier is empty: every branch visited, nothing silently assumed.
Summarise the settled decisions and do not act on them until the user confirms you have reached a
shared understanding. Then suggest the next step: `/to-spec` for work spanning several sessions,
`prototype` when a question can only be settled by running code, or `/implement` for work that
fits in one session.
