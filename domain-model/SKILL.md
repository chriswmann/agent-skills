---
name: domain-model
description: >
  Build and sharpen a project's domain language. Use when a term is fuzzy, overloaded or
  disputed, when writing or editing GLOSSARY.md, or when recording or editing an ADR.
---

# Domain model

Keep one shared language between the user, the code and the agent, and record the decisions a
future reader would otherwise question. A settled term saves words in every later session: "the
materialisation cascade" instead of a sentence of explanation.

Reading `GLOSSARY.md` for vocabulary is a habit every skill has. This skill is for changing the
model.

## Files

- **`GLOSSARY.md`** at the repository root. If a `GLOSSARY-MAP.md` exists, the repository has
  several contexts; the map says where each context's glossary lives.
- **`docs/adr/NNNN-slug.md`**, numbered from the highest existing number plus one.

Create either only when there is something to write in it.

## During a conversation

- **Challenge against the glossary.** When the user uses a term in a way that conflicts with
  `GLOSSARY.md`, say so at once: "The glossary defines *cancellation* as X; you seem to mean Y.
  Which is it?"
- **Sharpen fuzzy words.** Propose one precise term for a vague or overloaded one: "By *account*,
  do you mean the Customer or the User?"
- **Test with scenarios.** Invent concrete edge cases that force the boundary between two concepts
  into the open.
- **Check the code.** When the user says how something works, check that the code agrees, and
  surface any contradiction.
- **Write as you go.** Update `GLOSSARY.md` the moment a term is settled.

## Glossary format

```markdown
# <Context name>

<One or two sentences: what this context is and why it exists.>

## Language

**Order**:
A request by a **Customer** for one or more products.
_Avoid_: purchase, transaction
```

- Pick one word per concept and list the rejected synonyms under `_Avoid_`.
- One or two sentences per term, saying what it is, not what it does.
- Bold other glossary terms inside a definition.
- Only terms specific to this project. General programming concepts stay out.
- No implementation detail. The glossary is not a spec or a scratch pad.

## ADRs

Offer an ADR only when all three hold:

1. **Hard to reverse**: changing course later would cost real effort.
2. **Surprising without context**: a reader of the code would ask why it was done this way.
3. **A real trade-off**: there were genuine alternatives.

Good candidates: architectural shape, integration between contexts, technology with lock-in,
ownership boundaries, deliberate deviations from the obvious path, constraints invisible in the
code, and non-obvious rejected alternatives.

An ADR can be one paragraph:

```markdown
# <Short title of the decision>

<Context, what was decided, and why, in one to three sentences.>
```

Add `Status`, `Considered options` or `Consequences` only when they carry information.
