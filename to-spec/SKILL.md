---
name: to-spec
description: Turn the current conversation into a written spec. Synthesis only, no new interview.
disable-model-invocation: true
---

# To spec

Write down what the conversation has already settled, so the build can be checked against it and
a fresh session can pick it up. Do not interview the user again; if something essential is
missing, name it in **Open questions** and ask once at the end.

## Where it goes

Write to `docs/specs/<slug>/spec.md` unless `CLAUDE.md` names another place or the user asks for
a GitHub issue. Use the project's `GLOSSARY.md` vocabulary throughout, and respect the ADRs in
the area being changed.

## Steps

1. **Read the code the spec touches**, if you have not already, so module names and current
   behaviour are right.
2. **Propose the test seams.** A seam is the public interface the tests will exercise. Prefer
   existing seams, and the highest one that reaches the behaviour; the fewer the better. Give each
   a line on what it catches and what it misses, and confirm them with the user. (See
   `codebase-design` for the vocabulary.)
3. **Write the spec** with the template below and give the user its path.

## Template

```markdown
# <Title>

## Problem
<The problem, from the user's side.>

## Solution
<The solution, from the user's side.>

## Behaviour
<A numbered list of observable behaviours, as complete as the conversation allows. Each one
specific enough to test: "Given X, when Y, then Z.">

## Decisions
- Modules built or changed, and their interfaces
- Data and schema changes, API contracts
- Architectural choices (link the ADR where one exists)

## Testing
- Seams under test, as confirmed
- Prior art: similar tests already in the repository

## Out of scope

## Open questions

## Further notes
```

No file paths or code snippets in **Decisions**: they go stale. The exception is a type, schema
or state machine from a prototype that states a decision more exactly than prose; trim it to the
decision and say where it came from.

Next step: `/to-tickets` to split the spec, or `/implement` if it fits in one session.
