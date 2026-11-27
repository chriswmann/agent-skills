---
name: diagnose
description: >
  Disciplined loop for hard bugs and performance regressions: build a red feedback loop,
  minimise, hypothesise, instrument, fix with a regression test. Use when the user says
  "debug"/"diagnose", or reports something broken, failing, flaky or slow.
---

# Diagnose

A gated loop for bugs that resist a first look. Skip a phase only with a stated reason. Read
`GLOSSARY.md` and the ADRs near the code first.

**Redact.** Replace every secret in commands, output and captured artefacts with `<REDACTED>`.
Build loops that read credentials from the environment.

## 1. Build a feedback loop

This phase is most of the work. With a **tight** loop that goes **red** on this bug, the cause will
be found; without one, reading code produces theories, not fixes.

Ways to build one, roughly in order of preference:

1. A failing test at the seam that reaches the bug (`pytest -k`, `cargo test <name>`).
2. A `curl` or `httpx` script against a running dev server.
3. A CLI run on a fixture, diffed against known-good output.
4. A Playwright script that drives the UI and asserts on the DOM, console or network.
5. A captured request, payload or event log replayed through the code path.
6. A throwaway harness: the smallest subset of the system that reaches the bug in one call.
7. A property or fuzz loop (`hypothesis`, `proptest`) for "sometimes wrong".
8. A bisection script for `git bisect run` (or `jj` equivalents) between a good and a bad state.
9. A differential run: the same input through two versions or configurations, outputs diffed.
10. Last resort: a script that walks a human through the manual steps and captures their output.

Then tighten it: faster (narrow the scope, cache setup), sharper (assert the exact symptom, not
"did not crash"), more deterministic (fix the seed, the clock, the file system). For a flaky bug,
raise the reproduction rate (loop it, parallelise, add load) until it is debuggable.

**Gate.** Name one command you have already run, with its redacted output, that drives the real
code path, asserts the user's exact symptom, gives the same verdict every run, finishes in
seconds and needs no human. No such command, no phase 2. If you cannot build one, stop, list what
you tried, and ask for access, a captured artefact or permission to instrument.

## 2. Reproduce and minimise

Run the loop and confirm it shows the failure the user described, not a nearby one. Then cut
inputs, callers, configuration and steps one at a time, re-running after each cut, until every
remaining element is load-bearing.

## 3. Hypothesise

Write three to five ranked, falsifiable hypotheses before testing any: "If X is the cause, then
changing Y will make the bug disappear." A hypothesis without a prediction is discarded. Show the
list to the user, since they often re-rank it at a glance; carry on with your ranking if they are
away.

## 4. Instrument

Each probe tests one prediction; change one variable at a time. Prefer a debugger (`pdb`,
`breakpoint()`, `rust-gdb`, `lldb`) to logs, and targeted logs to logging everything. Tag every
debug line with a unique prefix such as `[DEBUG-a4f2]` so cleanup is one `grep`.

For performance, measure before changing anything: a timing harness, `py-spy`, `cargo flamegraph`,
a query plan. Then bisect.

## 5. Fix with a regression test

If there is a seam where a test reproduces the real bug pattern, turn the minimised repro into a
test there, watch it fail, fix, watch it pass, then re-run the original loop. If the only seam is
too shallow to reproduce the bug, do not write a falsely reassuring test: record that the
architecture prevents locking the bug down, and suggest `codebase-design`.

## 6. Clean up

- [ ] The original loop no longer reproduces the bug.
- [ ] The regression test passes, or the missing seam is recorded.
- [ ] No `[DEBUG-` lines remain.
- [ ] Throwaway harnesses are deleted or clearly marked.
- [ ] The commit message states the hypothesis that proved correct.
