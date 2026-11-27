---
name: bayesian-workflow
description: Use when starting a Bayesian analysis, deciding what to model or which likelihood and structure to use, changing priors after sampling trouble, or before reporting posterior results.
---

# Bayesian Workflow

## Overview

Distilled modelling judgement for the two ends of an analysis: framing the
question before any code, and guarding the conclusion after it. The modelling
loop in between (start simple, prior and posterior predictive checks,
diagnostics, expanding and comparing with LOO) belongs to pymc-modeling.

**REQUIRED SUB-SKILL (PyMC projects):** pymc-modeling for the modelling loop,
API, sampler, and diagnostics code.

## Before Any Code

1. **State the estimand.** What quantity, for which population, to inform
   what decision? If the data for it doesn't exist, stop and get it — never
   substitute simulated data without labelling it.
2. **Sketch the generative story.** How did each observation come to exist?
   Likelihood, link, and hierarchy fall out of the story — not from a menu
   of models.

## Checking Against the Question

In posterior predictive checks, the model need not reproduce every feature
of the data — only the features the question depends on (tails for risk,
seasonality for forecasts, group differences for comparisons). Choose those
features from the estimand before looking at the fit.

## Red Flags — STOP

- Interpreting parameters before the diagnostics gate passes.
- Simulated data feeding a conclusion presented as real analysis.
- Adding model complexity because it's interesting, not because a check
  failed.
- Reporting a point estimate where the decision needs the full posterior
  (tail risk, intervals, probability of direction).
- "It converged after I changed the priors" without a generative reason for
  the new priors. Fix the geometry; do not tighten priors merely to force
  convergence.
