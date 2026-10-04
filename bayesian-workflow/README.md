# bayesian-workflow

A Claude Code skill capturing the Bayesian modelling judgement that sits
around the modelling loop: state the estimand and the generative story before
any code, check the model against the features the question depends on, and
stop before a conclusion outruns its evidence.

It is the judgement layer over the `pymc-modeling` skill, which covers the
modelling loop itself and the PyMC API, sampler, and diagnostics specifics.
This skill decides *what* to model and *when* a result may be trusted;
`pymc-modeling` covers *how* to build, fit, and check it.

## Contents

- `SKILL.md` — the skill itself: framing steps before any code, posterior
  predictive checks tied to the question, and red-flag stop conditions.

## Installation

Symlink the skill into the `skills` directory of your Claude Code config home
(`$CLAUDE_CONFIG_DIR`, or `~/.claude` if you have not set it):

```sh
ln -s /path/to/skills/bayesian-workflow "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/bayesian-workflow"
```

## Triggers

Invoked when starting a Bayesian analysis, deciding what to model or which
likelihood and structure to use, changing priors after sampling trouble, or
before reporting posterior results.
