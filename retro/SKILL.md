---
name: retro
description: Look back over a coding session and propose changes to the agent's environment, worst problems first.
disable-model-invocation: true
---

# Retro

Find what in the **environment** (not the code) made this session slower or worse than it needed
to be, and propose the change that would have prevented it. Default to the current session; if the
user names another, read its transcript under `~/.claude/projects/`.

## Steps

1. **Read the session**: where time went, which mistakes were made, which tool calls were
   expensive, where the agent had to ask or guess.
2. **Read the environment**: `CLAUDE.md` and `AGENTS.md` (project and `~/.claude/`), the
   repository's check commands (`pyproject.toml`, `Cargo.toml`, `Makefile`, CI workflows,
   pre-commit configuration), and any coding standards file.
3. **Find candidates** in the categories below.
4. **Present them** most severe first, each with: what happened in the session, the proposed
   change, and where it goes. Apply nothing without the user's agreement.

## Categories

- **Navigation.** The agent took long to find something. Propose a one-line pointer in
  `CLAUDE.md` to the file or doc that holds it.
- **Automated checks.** The agent made a mistake a tool could have caught. Look first for a check
  that exists but is not wired up or is broken. A repository with no guardrail at all (no
  pre-commit hook and no CI running lint, types and tests) is itself a finding.
- **Coding standards.** The review missed something. If the rule is mechanical (a banned API, an
  import shape, a file location), propose a lint rule or hook, not prose. Keep a standards file
  for genuine judgement calls; it is read at review time, not loaded into every session.
- **Steering files.** `CLAUDE.md` holds rules that belong in a check or a standards file, or
  instructions the model follows anyway (no-ops). Propose moving or deleting them.
- **Tool economy.** A tool or MCP server returned far more than was needed. Propose a narrower
  command, a flag, or a script.
- **Information access.** Something crucial was invisible: server logs, a read-only view of a
  third-party service, a fixture. Propose how to expose it.

## Placement rule

`CLAUDE.md` is loaded into every session, so it should hold little beyond pointers. The reviewer
works from a diff with little context pressure, so standards belong to review, not to
implementation. Mechanical rules belong to tools. See `writing-skills` for how to word whatever
is added.
