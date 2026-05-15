## Summary

Describe what this PR improves.

## Type of change

- [ ] Skill instruction update
- [ ] New example or decision trap
- [ ] Evidence rubric update
- [ ] Scanner/script improvement
- [ ] Semgrep rule update
- [ ] Documentation or install improvement

## Legacy-support reasoning

If this changes the skill's adjudication behavior, explain how it affects the verdict process:

- affected verdicts:
- risk level affected:
- evidence standard changed:
- likely false positives/false negatives:

## Checklist

- [ ] `skills/legacy-support-adjudication/SKILL.md` still has valid frontmatter with `name` and `description`.
- [ ] New guidance does not imply local static search alone is enough for risky removals.
- [ ] Examples end with an actionable verdict.
- [ ] Scripts compile on Python 3.9+.
- [ ] README links still resolve.
