---
name: review-change
description: >
  Two-axis review of the changes since a fixed point: Standards (does it follow this
  repository's rules and avoid common smells?) and Spec (does it do what the ticket or spec
  asked?), run as separate subagents. Use when reviewing a branch, PR or work in progress, or
  after implementing a ticket.
---

# Review a change

Review a change on two separate axes, so that one cannot hide the other: code that follows every
rule but builds the wrong thing fails **Spec**; code that does exactly what was asked but breaks
the project's conventions fails **Standards**.

## 1. Pin the fixed point

Use what the user named (a branch, commit, tag, `main`, `HEAD~3`); if nothing, use the merge base
with the default branch. With git: `git diff $(git merge-base <base> HEAD)` and
`git log <base>..HEAD --oneline`. Where `.jj/` exists:
`jj --no-pager diff --git --from 'fork_point(<base>@origin | @)'`. Confirm the ref resolves and the
diff is non-empty before going further.

## 2. Find the spec

In order: issue or ticket references in the commit messages; a path the user gave; a spec under
`docs/specs/` matching the branch or feature; the plan agreed in this conversation. If none exists, the
Spec axis reports "no spec available".

## 3. Find the standards

Every file that says how code should be written: `CODING_STANDARDS.md`, `CONTRIBUTING.md`,
`CLAUDE.md`, `AGENTS.md`, lint configuration. Skip anything a tool already enforces.

On top of those, always apply this **smell baseline** (Fowler, *Refactoring*, chapter 3). Each is a
judgement call, labelled "possible", and a documented repository rule overrides it.

- **Mysterious name**: a name that does not say what the thing is or does. Rename it.
- **Duplicated code**: the same logic in more than one hunk. Extract it.
- **Feature envy**: a function that uses another object's data more than its own. Move it.
- **Data clump**: the same few values always passed together. Give them a type.
- **Primitive obsession**: a `str` or `int` standing in for a domain concept. Give it a type
  (a `NewType`, an enum, a Rust newtype).
- **Repeated switch**: the same `match`/`if` cascade on the same type in several places. Use one
  table or polymorphism.
- **Shotgun surgery**: one logical change spread across many files. Gather what changes together.
- **Divergent change**: one module edited for unrelated reasons. Split it.
- **Speculative generality**: parameters, hooks or abstractions the spec does not need. Remove them.
- **Message chain**: `a.b().c().d()` that the caller should not depend on. Hide it behind a method.
- **Middle man**: a module that only delegates. Call the target directly.

## 4. Run both axes in parallel

Start two subagents in one message, each with a fresh context.

- **Standards** gets the diff command, the commit list, the standards files and the smell baseline
  pasted in full. Brief: "For each hunk, report breaches of a documented rule (cite file and rule)
  and possible baseline smells (name it, quote the hunk). Separate hard breaches from judgement
  calls. Under 400 words."
- **Spec** gets the diff command, the commit list and the spec. Brief: "Report (a) requirements
  missing or partly done, (b) behaviour nobody asked for, (c) requirements that look done but look
  wrong. Quote the spec line for each. Under 400 words."

## 5. Report

Show the two reports under `## Standards` and `## Spec`, lightly edited, without merging or
re-ranking across them. End with one line: the number of findings on each axis and the worst
finding within each.

If the user asks for fixes, apply the hard findings and list the judgement calls for them to
decide.
