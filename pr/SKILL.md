---
name: pr
description: Use when writing a pull request description or commit summary for a reviewer.
---

# Pull request body

A reviewer should see what changed, that it works, and how risky it is to merge, in the time it
takes to scroll once. Use `GLOSSARY.md` terms, skip preamble, keep prose short. If the repository
has a PR template, fill in its headings with this content instead.

```markdown
## Summary
<one or two sentences, then the smallest visual that makes the change clear>

## Evidence
- **Before:** <failing test, output or screenshot>
- **After:** <passing test, output or screenshot>

## Merge danger
**Door:** one-way | two-way. <what makes it so>
**Blast radius:** <one word>. <who or what could break>
```

## Summary visual

Pick one, occasionally two, and keep only the parts that matter to the point:

- **Pseudocode** for logic.
- **A call tree** for control flow (`submit → create_session → persist_prompt`).
- **A shallow file tree** for a change in where responsibilities live.
- **A `diff` block over one of the above** when the surrounding shape already exists and the point
  is what moved.
- **Mermaid** for interaction between components.

## Evidence

Screenshots for visual changes, when the environment can produce them. Otherwise execution: the
test that now passes (and failed before), or the command output before and after. Name the test.

## Merge danger

- **Two-way door**: cheap to roll back (a revert restores the old state).
- **One-way door**: hard to reverse: data migrations, deletions, published APIs, external side
  effects.
- **Blast radius**: what could be affected if it is wrong: callers, consumers of an API, stored
  data, performance, deployments.
