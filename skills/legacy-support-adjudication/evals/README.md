# Evaluations

This directory contains two eval sets for the `legacy-support-adjudication` skill, following the patterns in:

- [Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills)
- [Optimizing skill descriptions](https://agentskills.io/skill-creation/optimizing-descriptions)

## `trigger_queries.json` — does the description trigger the skill?

20 realistic user queries labeled `should_trigger: true | false`. Roughly evenly split between positive and negative cases, with several **near-misses** (queries that share keywords with the skill but should NOT trigger it) to test that the description is precise rather than just broad.

Each entry includes a `rationale` field so future maintainers can see what each case is meant to probe.

### Suggested split for description optimization

Per the optimizing-descriptions guide, split into train (~60%) and validation (~40%) sets and keep the split fixed across iterations. Suggested:

- **Train (12):** indices `0, 1, 2, 3, 8, 9, 10, 11, 12, 13, 14, 15`
- **Validation (8):** indices `4, 5, 6, 7, 16, 17, 18, 19`

Both sets contain a mix of should-trigger and should-not-trigger queries.

### Running

The exact invocation depends on your agent client. The optimizing-descriptions guide shows the general pattern (run each query 3 times, compute a trigger rate per query, pass if rate > 0.5).

## `evals.json` — does the skill produce good verdicts?

5 PR-review scenarios derived from cases in `examples/example_verdicts.md`. Each scenario has:

- A realistic reviewer prompt.
- An `expected_output` describing what a good verdict looks like.
- Concrete `assertions` that can be graded against actual outputs.

The cases span all five verdicts (RETAIN, DEPLOY OBSERVABILITY, DEPRECATE, QUARANTINE, REMOVE) and all four risk tiers (P0–P3), so a passing run gives broad coverage of the skill's behavior space.

### Running

Per the evaluating-skills guide, run each case twice:

1. **With skill:** point the agent at this skill folder and the prompt.
2. **Without skill (baseline):** same prompt, no skill.

Save outputs to `workspace/iteration-N/eval-<id>/with_skill/` and `.../without_skill/` respectively, grade each assertion (`grading.json`), and aggregate into `benchmark.json`. The delta between with-skill and without-skill pass rates is the skill's value.

## Adding cases

When you correct the skill after a real review goes wrong, add the failing scenario here. That's the direct way the evaluating-skills guide recommends to improve a skill: turn each correction into a regression test.
