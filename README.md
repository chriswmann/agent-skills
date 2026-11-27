# Agent skills

Skills for Claude Code, written for Python and Rust work, adapted from Matt Pocock's MIT-licensed
[skills](https://github.com/mattpocock/skills). See [CREDITS.md](CREDITS.md).

## Install

```bash
./install.sh                    # offers to search $HOME for Claude profiles, then asks which to use
./install.sh --all              # every profile found, no questions
./install.sh ~/.claude-work     # named profiles (or skills folders), no questions
```

A profile is a Claude config directory: `~/.claude`, or another directory at the top of `$HOME`
used through `CLAUDE_CONFIG_DIR` (such as `~/.claude-work`). Each skill folder is symlinked into
`<profile>/skills`, so edits in this repository take effect in the next session. Existing skills
with the same name are skipped, not overwritten. To install into one project only, pass its
skills directory: `./install.sh path/to/project/.claude/skills`.

## The skills

**Model-invoked** skills have a description in context, so Claude reaches for them when the task
fits, and other skills can call them. **User-invoked** skills run only when you type `/name` and
cost no context otherwise.

| Skill | Invoked by | What it does |
| --- | --- | --- |
| `flow` | user | Map of the skills and the order to use them. Start here if unsure. |
| `grill` | model | Relentless interview over the design tree, one round per frontier, until every branch is resolved. Writes nothing. |
| `grill-docs` | user | `grill` plus `domain-model`: the same interview, keeping `GLOSSARY.md` and ADRs current. |
| `domain-model` | model | Keep `GLOSSARY.md` and ADRs current as terms and decisions settle. |
| `prototype` | model | Throwaway code that answers one design question. |
| `to-spec` | user | Turn the conversation into `docs/specs/<slug>/spec.md`. |
| `to-tickets` | user | Split a spec into tracer-bullet tickets with blockers. |
| `implement` | user | Build one ticket test-first, run the checks, review, commit. |
| `tdd` | model | Red-green loop at agreed seams; good and bad tests in Python and Rust. |
| `diagnose` | model | Gated debugging: a red feedback loop before any theory. |
| `review-change` | model | Standards and Spec review in two parallel subagents, with a smell baseline. |
| `pr` | model | PR body: summary visual, before/after evidence, merge danger. |
| `explain-diff` | user | Explain a change as a page with a quiz. |
| `codebase-design` | model | Deep-module vocabulary; surveys for deepening opportunities. |
| `handoff` | user | Write a handoff document for a fresh session or colleague. |
| `retro` | user | Propose environment changes after a session. |
| `wait-what` | user | Re-explain the last message plainly. |
| `setup-audit` | user | Measure a profile's context load and sediment; change only what you pick, retiring rather than deleting. |
| `writing-skills` | model | How to write skills and `CLAUDE.md` for agents. |

## Conventions

- Specs and tickets live in `docs/specs/<slug>/` unless a project's `CLAUDE.md` says otherwise.
- Checks are discovered from the repository (`pyproject.toml`, `Cargo.toml`, CI) rather than
  assumed.
- `jj` is preferred where a `.jj/` directory exists.
- Scripts are single-file Python run with `uv run --script`.
