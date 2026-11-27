---
name: implement
description: Build one ticket or a small spec test-first, check it, review it and commit it.
disable-model-invocation: true
---

# Implement

Build the work the user points at: a ticket file, a spec, a GitHub issue, or the plan agreed in
this conversation.

1. **Load the work.** Read the ticket or spec in full and state its title and acceptance criteria
   before starting. If its blockers are not done, say so and stop. If the reference is ambiguous,
   ask.
2. **Find the checks.** Read the repository's own commands: `pyproject.toml`, `Makefile`,
   `justfile`, `Cargo.toml`, CI workflows, `CLAUDE.md`. Typical sets: `ruff check`, `ruff format
   --check`, `mypy` or `pyright`, `pytest`; `cargo fmt --check`, `cargo clippy -- -D warnings`,
   `cargo test`. Use what the repository uses.
3. **Build with `tdd`**, one slice at a time, at the seams the spec agreed. Run the type checker
   and the single test file you are working on after every slice.
4. **Run everything once at the end**: the full test suite and every check from step 2. All
   green, or report exactly what fails.
5. **Review with `review-change`** against the ticket or spec. Fix the hard findings; list the judgement
   calls for the user.
6. **Tick the acceptance criteria** in the ticket file, and set its status to done.
7. **Commit** to the current branch (or `jj commit` where `.jj/` exists) with a message that says
   what now works and why. Do not push unless the user asks.

Report: what was built, the check results, review findings left open, and the next unblocked
ticket.
