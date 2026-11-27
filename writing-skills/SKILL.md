---
name: writing-skills
description: >
  How to write documents agents read. Use when creating or editing a skill (SKILL.md), a
  CLAUDE.md or AGENTS.md, or any doc an agent reaches through a pointer.
---

# Writing for agents

Every document an agent reads spends one of two budgets. **Context load** is anything always in
the window: a `CLAUDE.md` line, a skill's description. It costs tokens and attention every turn
whether or not it is used. **Cognitive load** falls on the human, who must remember what exists
and when to reach for it. Spend context load only where the agent must find the material itself.

## Pointers

A skill's description and a line in `CLAUDE.md` that names a file are the same thing: a
**pointer** that says what the material is and when to reach it. Its wording decides whether the
agent reaches it.

- Lead with the word that should trigger it.
- One trigger per distinct case. Synonyms for the same case are one trigger.
- Leave out what the body already says.

If a must-have document is not being reached, sharpen the pointer before inlining the material.

## Structure

- **Steps** are what the agent does, in order. **Reference** is consulted on demand. Keep steps in
  the main file; move reference that only some cases need into a sibling file behind a pointer.
- Keep a concept's definition, rules and caveats together under one heading.
- End every step on a **completion criterion** the agent can check ("every modified model listed",
  not "understanding reached"). A vague criterion invites stopping early.
- Too long is a failure even when every line is true. Split by case or by sequence.

## Wording

- Use a **leading word** the model already knows (*tracer bullet*, *red*, *tight*, *frontier*)
  instead of restating an idea in a sentence. Repeat the word, not the explanation.
- State the behaviour you want. A prohibition puts the unwanted behaviour into context; keep
  "never" for hard guardrails and pair it with the positive.
- Cut **no-ops**: instructions the model follows anyway. Delete the whole sentence.
- Keep each fact in one place. Do not restate what the environment already says (`--help`,
  `pyproject.toml`, the directory layout); write down what cannot be looked up: conventions,
  reasons, gotchas.
- Prune stale lines. Adding feels safe and removing feels risky; that is how sediment builds.

## Skill mechanics

- **Model-invoked** (no `disable-model-invocation`): the description is always loaded, so the
  agent and other skills can reach it. Write the description for the model, with its triggers.
  Use it for reference other skills need and for work the agent should start unprompted.
- **User-invoked** (`disable-model-invocation: true`): no context cost, reachable only by typing
  `/name`; other skills cannot call it. Write the description as a one-line summary for the human.
- A user-invoked skill may call model-invoked ones, never another user-invoked one. Reference
  shared by two user-invoked skills goes in a plain file or a model-invoked skill.
- Paths inside a skill are relative to its own directory. Scripts take arguments and print
  results; they never depend on the caller's working directory.
- When user-invoked skills grow past what you can remember, add one router skill that lists them
  (`flow` in this collection).
