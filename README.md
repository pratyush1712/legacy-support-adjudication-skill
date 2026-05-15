# Legacy Support Adjudication

[![Skill](https://img.shields.io/badge/Agent%20Skill-legacy--support--adjudication-blue)](./SKILL.md)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](./scripts/legacy_support_scan.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Semgrep Rules](https://img.shields.io/badge/Semgrep-rules-informational)](./semgrep/legacy-support-patterns.yml)

A professional agent skill for code-review agents that need to decide whether backward-compatibility logic is still required or has become removable technical debt.

This is not a dead-code detector. It is a **consumer-aware deprecation analysis** skill: it traces old behavior across code, data, clients, jobs, configs, feature flags, migrations, runtime evidence, and support contracts before recommending whether to keep or remove it.

## What it helps reviewers decide

Use this skill when a PR touches compatibility logic such as:

- old API versions, response shapes, or field aliases
- database migration shims, old columns, dual reads, dual writes, or backfills
- mobile/client fallbacks and stale cached payload handling
- frontend local-storage/session migrations
- old enum normalization, webhook formats, import/export formats, or event replay support
- feature-flag rollback paths
- retired runtime, package-manager, browser, OS, or CI/build support

The skill produces one of five verdicts:

| Verdict | Meaning |
|---|---|
| **RETAIN** | The compatibility contract still exists. |
| **DEPLOY OBSERVABILITY** | The path may be removable, but runtime/data evidence is missing. |
| **DEPRECATE** | Consumers may still exist; create a migration and sunset path. |
| **QUARANTINE** | Isolate the legacy path behind a named boundary while evidence is gathered. |
| **REMOVE** | Evidence shows the support contract is closed. |

## Why this exists

Compatibility code often survives because nobody can prove it is safe to remove. Reviewers see a branch named `legacy`, `compat`, or `fallback`, but the real dependency may live in old mobile clients, persisted database rows, delayed jobs, cached payloads, generated SDKs, replayable events, customer integrations, rollback plans, or migration history.

This skill gives agents a repeatable review method so they do not approve risky deletions based only on local static search.

## Install

### Skills CLI

The recommended install path is the Skills CLI. The Skills directory documents `npx skills add <owner>/<skill-name>` as the standard install command, and leaderboard ranking is based on aggregate anonymous installs from this command.

Find the skill:

```bash
npx skills find legacy support adjudication
```

Install directly from GitHub:

```bash
npx skills add pratyush1712/legacy-support-adjudication-skill
```

You can also search broader terms:

```bash
npx skills find code review
npx skills find deprecation
npx skills find compatibility
npx skills find technical debt
```

### Claude Code personal skill

```bash
mkdir -p ~/.claude/skills/legacy-support-adjudication
git clone https://github.com/pratyush1712/legacy-support-adjudication-skill.git \
  ~/.claude/skills/legacy-support-adjudication
```

Then invoke it directly:

```text
/legacy-support-adjudication
```

Or ask naturally:

```text
Review this PR and decide whether the legacy fallback can be removed.
```

### Project-local skill

```bash
mkdir -p .claude/skills
git submodule add https://github.com/pratyush1712/legacy-support-adjudication-skill.git \
  .claude/skills/legacy-support-adjudication
```

### Manual install

Copy this repository into any skill directory that expects a `SKILL.md` entrypoint.

```text
legacy-support-adjudication/
├── SKILL.md
├── resources/
├── examples/
├── scripts/
└── semgrep/
```

## Quick start

From a repository you want to review:

```bash
python ~/.claude/skills/legacy-support-adjudication/scripts/legacy_support_scan.py \
  --root . \
  --format json \
  --output legacy-support-candidates.json

python ~/.claude/skills/legacy-support-adjudication/scripts/render_lsa_report.py \
  legacy-support-candidates.json \
  --output legacy-support-report.md
```

Then ask your agent:

```text
Use the legacy-support-adjudication skill. Review legacy-support-report.md and the current diff. For each candidate, return a verdict with evidence, confidence, risk, and required next action.
```

## Example agent prompt

```text
Use the legacy-support-adjudication skill to review this PR.

Focus on compatibility logic, migration shims, deprecated API bridges, old schema handling, feature-flag fallbacks, old mobile/client support, and transitional formats.

Do not treat lack of local references as enough evidence for removal. Trace code, data, client, runtime, and owner evidence where relevant. End with the verdict block required by the skill.
```

See [`examples/agent_prompt.md`](./examples/agent_prompt.md) for a fuller version.

## Repository contents

| Path | Purpose |
|---|---|
| [`SKILL.md`](./SKILL.md) | Main skill instructions and invocation guidance. |
| [`resources/evidence_rubric.md`](./resources/evidence_rubric.md) | Evidence levels, risk classes, and removal thresholds. |
| [`resources/legacy_patterns.yml`](./resources/legacy_patterns.yml) | Pattern taxonomy and search vocabulary. |
| [`resources/report_template.md`](./resources/report_template.md) | Copyable review verdict template. |
| [`resources/review_comment_templates.md`](./resources/review_comment_templates.md) | Reusable code-review comments. |
| [`examples/example_verdicts.md`](./examples/example_verdicts.md) | Complex real-world case studies and sample verdicts. |
| [`examples/decision_traps.md`](./examples/decision_traps.md) | Common false-removal traps. |
| [`scripts/legacy_support_scan.py`](./scripts/legacy_support_scan.py) | No-dependency Python scanner for compatibility-debt candidates. |
| [`scripts/git_support_archaeology.sh`](./scripts/git_support_archaeology.sh) | Git-history helper for finding when support was introduced. |
| [`scripts/render_lsa_report.py`](./scripts/render_lsa_report.py) | Converts scanner JSON into review-ready Markdown. |
| [`semgrep/legacy-support-patterns.yml`](./semgrep/legacy-support-patterns.yml) | Starter Semgrep rules for compatibility patterns. |

## Run the scanner

```bash
python scripts/legacy_support_scan.py --root . --format json --output legacy-support-candidates.json
python scripts/render_lsa_report.py legacy-support-candidates.json --output legacy-support-report.md
```

For a direct Markdown scan without the intermediate JSON file:

```bash
python scripts/legacy_support_scan.py --root . --format markdown --output legacy-support-scan.md
```

The scanner finds candidates. It does **not** approve deletion. Agents should use the evidence rubric before making a removal recommendation.

## Run Semgrep rules

```bash
semgrep --config semgrep/legacy-support-patterns.yml .
```

## What good output looks like

```markdown
### Legacy Support Adjudication Verdict

**Verdict:** DEPLOY OBSERVABILITY  
**Confidence:** Medium  
**Risk:** P1  
**Legacy contract:** Accepts old mobile payload field `user_id` in addition to `userId`.  
**Consumer reality:** No current web/backend references found, but mobile versions older than 4.8 were not checked.  
**Producer reality:** Current backend emits only `userId`, but old mobile clients may still send `user_id`.  
**Evidence:**
- Static search found no current internal producer.
- API schema no longer documents `user_id`.
- No runtime metric currently records fallback usage.

**Required before merge:**
- Add fallback-hit metric for 14–30 days.
- Check mobile minimum supported version and app-store active-version distribution.

**Recommended cleanup path:**
- Keep fallback for now, instrument it, and remove only after observed usage is zero over the agreed window.
```

## Design principles

- Evidence beats vibes.
- Compatibility support is a contract, not just code.
- Current writers do not define all possible inputs.
- Missing telemetry is not proof of zero usage.
- Good cleanup is staged, reversible, and easy to audit later.

## Contributing

Contributions are welcome. Good additions include:

- new nuanced examples
- more language/framework-specific Semgrep rules
- scanner heuristics with low false-positive rates
- review templates for specific domains like GraphQL, mobile, Kafka, Rails, Django, FastAPI, Next.js, Postgres, or OpenAPI

See [`CONTRIBUTING.md`](./CONTRIBUTING.md).

## License

MIT License. See [`LICENSE`](./LICENSE).
