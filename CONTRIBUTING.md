# Contributing

Thank you for improving Legacy Support Adjudication.

This repository is intentionally small and practical. The best contributions make code-review agents better at deciding whether compatibility support is still required.

## Good contributions

Useful additions include:

- nuanced examples in `examples/example_verdicts.md`
- new traps in `examples/decision_traps.md`
- better review comment templates
- scanner heuristics with low false-positive rates
- Semgrep rules for common stacks
- evidence rubrics for specific domains such as GraphQL, REST, mobile, Postgres, Kafka, Celery, Rails, Django, FastAPI, Next.js, or Terraform

## Principles

Before adding guidance, check that it follows the skill's core principles:

1. Evidence beats vibes.
2. Compatibility support is a contract, not just code.
3. Current writers do not define all possible inputs.
4. Missing telemetry is not proof of zero usage.
5. Good cleanup is staged, reversible, and easy to audit later.

## Example style

Examples should be realistic and verdict-oriented. Prefer this structure:

```markdown
## Case: Old mobile payload field

**Situation:** ...
**Trap:** ...
**Evidence to collect:** ...
**Verdict:** DEPLOY OBSERVABILITY
**Why:** ...
**Review comment:** ...
```

## Scanner changes

The scanner is intentionally heuristic. It should find candidates, not prove removability.

When changing scanner behavior:

- keep it dependency-light
- avoid repo-specific assumptions
- prefer transparent output over clever inference
- document new pattern categories in `resources/legacy_patterns.yml`
- add or update example output if behavior changes

## Semgrep rules

Rules should favor useful candidate discovery over aggressive blocking. Use clear messages that ask for evidence rather than declaring code removable.

## Pull request checklist

Before opening a PR:

- [ ] `SKILL.md` still describes when the skill should be invoked.
- [ ] New examples end with an actionable verdict.
- [ ] New guidance does not imply local static search is enough for risky removals.
- [ ] Scripts still run on Python 3.9+.
- [ ] README links still point to existing files.
