---
name: to-tickets
description: Split a spec, plan or conversation into tracer-bullet tickets, each naming the tickets that block it.
disable-model-invocation: true
---

# To tickets

Break the work into **tickets**: thin vertical slices, each small enough for one fresh session,
each listing the tickets that must land before it can start.

## 1. Gather

Work from the conversation. If the user passes a spec path or issue, read all of it, including
comments. Read the code it touches if you have not, and use `GLOSSARY.md` terms in ticket titles.

Look for prefactoring: "make the change easy, then make the easy change". Prefactoring tickets go
first.

## 2. Slice

- Each ticket is a **tracer bullet**: a narrow but complete path through every layer it needs
  (schema, logic, interface, tests), never one layer on its own.
- Each ticket is demonstrable or verifiable on its own.
- Each ticket fits in one fresh context window.
- Each ticket lists its **blockers**. A ticket with none can start at once.

**Wide refactors are the exception.** A mechanical change that breaks every call site at once (a
renamed column, a retyped shared symbol) cannot land as a green vertical slice. Sequence it as
**expand, migrate, contract**: add the new form beside the old; migrate callers in batches, one
ticket per package or directory, each blocked by the expand; delete the old form in a ticket
blocked by every batch.

## 3. Check with the user

Show a numbered list: title, blocked by, and what the ticket makes work end to end. Ask whether
the granularity is right, whether each blocker genuinely gates its ticket, and whether any ticket
should be merged or split. Iterate until approved.

## 4. Write them

Default: one file per ticket at `docs/specs/<slug>/tickets/NN-<slug>.md`, numbered with blockers
first, beside the spec. If `CLAUDE.md` names another place or the user wants GitHub issues, use
that, with native sub-issues or "Blocked by" links.

```markdown
# NN: <Title>

**Makes work:** <the end-to-end behaviour, from the user's side>
**Blocked by:** <ticket numbers, or "none">
**Status:** ready

- [ ] <acceptance criterion>
- [ ] <acceptance criterion>
```

No file paths or code in tickets, for the same reason as in specs.

Next step: `/implement <ticket>` in a fresh session per ticket, blockers first.
