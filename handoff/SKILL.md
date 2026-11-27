---
name: handoff
description: Compact this conversation into a handoff document so another agent or session can continue the work.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

# Handoff

Write a handoff document summarising this conversation so a fresh agent can continue the work.

- **Tailor it.** If the user passed an argument, it describes what the next session will focus on;
  shape the document around that.
- **Reference, do not copy.** Anything already captured elsewhere (specs, tickets, ADRs, issues,
  commits, diffs) is referenced by path or URL, not repeated.
- **Suggest skills.** End with a "Suggested skills" section naming the skills the next agent should
  load.
- **Redact** API keys, passwords, connection strings and personal details.
- **Save it outside the workspace**, in the system temporary directory (`$TMPDIR`, else `/tmp`),
  and give the user the path.

A handoff is for moving the work somewhere else: a new directory, a different tool or agent, a
colleague, or a side task forked off mid-phase. To carry on in the same place with less context,
`/compact` is cheaper.
