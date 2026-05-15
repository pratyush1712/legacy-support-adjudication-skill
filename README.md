# Legacy Support Adjudication Skill Package

This package helps code-review agents decide whether backward-compatibility logic is still required or removable technical debt.

## Files

- `SKILL.md` — primary agent instructions.
- `resources/legacy_patterns.yml` — search taxonomy and evidence checklist.
- `resources/evidence_rubric.md` — evidence levels and risk thresholds.
- `resources/report_template.md` — copyable report format.
- `resources/review_comment_templates.md` — review comments for common situations.
- `examples/example_verdicts.md` — sample outputs.
- `examples/agent_prompt.md` — prompt wrapper for review agents.
- `scripts/legacy_support_scan.py` — heuristic candidate scanner.
- `scripts/git_support_archaeology.sh` — git history helper.
- `scripts/render_lsa_report.py` — JSON-to-markdown renderer.
- `semgrep/legacy-support-patterns.yml` — starter Semgrep rules.

## Quick start

From a repository root:

```bash
python /path/to/scripts/legacy_support_scan.py --root . --format markdown > lsa-scan.md
python /path/to/scripts/legacy_support_scan.py --root . --changed-only --base origin/main --format json > lsa.json
python /path/to/scripts/render_lsa_report.py lsa.json > lsa-review.md
bash /path/to/scripts/git_support_archaeology.sh legacyPayload src/api/user.ts > archaeology.md
```

With Semgrep:

```bash
semgrep scan --config /path/to/semgrep/legacy-support-patterns.yml .
```

## Important limitation

The scanner only finds candidates. It does not prove removability. Use the evidence rubric before recommending deletion.
