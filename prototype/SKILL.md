---
name: prototype
description: >
  Build throwaway code that answers one design question. Use when a state model, algorithm or
  UI cannot be settled on paper and needs something runnable to look at.
---

# Prototype

A prototype is throwaway code that answers one question. Write the question at the top of the
prototype before any code, and stop when it is answered.

## Pick the shape from the question

- **"Does this logic or state model behave right?"** A single script or one self-contained HTML
  file that drives the model through the awkward cases and prints the full state after every
  step. For Python, a `uv run --script` file with inline dependencies; for Rust, an example under
  `examples/` or a scratch crate. Include free-play controls and a few scripted walkthroughs of
  the hard cases.
- **"What should this look like?"** Several radically different variants (three is usual) on one
  page or route, switchable by a URL parameter or a small toolbar, so they can be compared side by
  side.

If the question is ambiguous and the user is away, choose by the surrounding code (backend module:
logic; page or component: UI) and state the assumption at the top.

## Rules

1. **Clearly throwaway.** Put it next to the code it informs, named so nobody mistakes it for
   production (`prototype_*.py`, `examples/proto_*.rs`, `/proto/...`).
2. **One command to run**, printed in the reply.
3. **No persistence** unless persistence is the question; then use a scratch file or database
   named so it is obviously disposable.
4. **No polish**: no tests, no error handling beyond what keeps it running, no abstractions.
5. **Show the state** after every action or variant switch.
6. **Capture the answer.** Write the verdict and the question it settled into the spec, ticket or
   an ADR. Commit the prototype to a `prototype/<name>` branch, not the main line, and point to it
   from the spec. Only the validated decision reaches the real code.
