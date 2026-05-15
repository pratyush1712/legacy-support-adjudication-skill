---
name: legacy-support-adjudication
description: "Use during code review when a change touches backward-compatibility logic, migration shims, deprecated API/version bridges, old schema or payload handling, feature-flag fallbacks, transitional formats, old client support, historical data readers, or retired runtime/build support. Trigger even when the reviewer doesn't name 'compatibility' or 'deprecation' directly — questions like 'can we delete this yet?', 'is this still needed?', 'old clients?', 'migration complete?', or 'probably dead code' on a diff qualify, as do PRs that delete or simplify code paths named legacy/compat/fallback/shim/v1/deprecated. Produces an evidence-based verdict: retain, instrument, deprecate, quarantine, or remove."
compatibility: "Requires Python 3.9+ and bash. Optional: Semgrep for the bundled ruleset. Works with any agent that can execute scripts."
---

# Legacy Support Adjudication

## Purpose

Use this skill when reviewing code that may exist mainly for historical compatibility. The goal is to decide whether the support contract is still real, not merely whether the code is locally reachable.

Backward compatibility often spans code, persisted data, mobile clients, public APIs, SDKs, background jobs, queues, feature flags, build systems, and rollback procedures. A safe review must trace those dependencies before approving removal.

The skill returns a concrete verdict with evidence, confidence, risk, and next action:

- **RETAIN** — the compatibility contract still exists.
- **DEPLOY OBSERVABILITY** — the path may be removable, but runtime or data evidence is missing.
- **DEPRECATE** — consumers may still exist; start a formal migration and sunset path.
- **QUARANTINE** — isolate the compatibility path while preserving behavior and collecting evidence.
- **REMOVE** — evidence shows the compatibility contract is closed.

## Invoke this skill when

A diff, PR, issue, or review discussion includes any of these signals:

- Names such as `legacy`, `compat`, `backcompat`, `fallback`, `old`, `v1`, `deprecated`, `migration`, `shim`, `adapter`, `normalize`, `upgrade`, `downgrade`, `transitional`, or `TODO remove`.
- Code accepting multiple field names, schema versions, API versions, enum names, payload formats, auth/session formats, client versions, storage layouts, or protocol variants.
- Database code involving old columns/tables, nullable historical fields, dual reads, dual writes, shadow fields, backfills, repair jobs, or migration cleanup.
- Frontend or mobile code normalizing historical API responses, old app versions, stale local storage/session keys, retired routes, or old deep links.
- CI/build/deployment logic for old runtimes, old package managers, retired browsers, old operating systems, release branches, or retired environments.
- Reviewer language like "can we delete this yet?", "is this still needed?", "old clients?", "migration complete?", "probably dead code", or "cleanup legacy path."

If you are uncertain whether a path matches one of these categories, consult `references/legacy_patterns.yml` for the full pattern taxonomy and search vocabulary.

## Core questions

For each candidate compatibility path, answer five questions:

1. **What old thing is supported?** Identify the exact legacy contract: endpoint, field, schema, enum, flag state, client version, file format, event shape, auth/session format, DB state, runtime, or deployment mode.
2. **Who still uses it?** Trace consumers across code, tests, generated clients, SDKs, data, jobs, queues, configs, dashboards, logs, docs, and owners.
3. **Can new inputs still produce it?** Check whether current systems can still create, receive, hydrate, import, replay, cache, restore, or roll back into the old shape.
4. **What breaks if it disappears?** Identify runtime errors, data loss, failed migrations, broken API clients, user-visible regressions, failed jobs, failed imports, rollout risk, and rollback risk.
5. **What evidence is enough?** Match the evidence requirement to the risk level. Do not require the same proof for a test-only shim and a public mobile API fallback.

## Evidence levels

Use the strongest evidence available. Lower confidence when a relevant layer cannot be inspected.

| Level | Evidence | Meaning |
|---|---|---|
| E0 | Suspicion only | Names, comments, or history suggest legacy support. Investigation starts here. |
| E1 | Local static references | Local search/AST shows direct references or absence of references. Useful but weak. |
| E2 | Cross-boundary static references | Related repos, clients, generated code, configs, scripts, tests, docs, or SDKs checked. |
| E3 | Data reality | DB rows, object storage, queues, events, imports, caches, local storage, or fixtures checked. |
| E4 | Runtime reality | Logs, traces, metrics, endpoint hits, feature-flag exposure, error reports, or access records checked over a representative window. |
| E5 | Contract/owner confirmation | API policy, support policy, migration notice, owner signoff, customer/integration confirmation, or release policy checked. |
| E6 | Staged validation | Dark disable, canary, shadow removal, kill switch, rollback, or staged rollout tested. |

Minimum standard:

- **P3 low-risk internal cleanup:** E1 plus tests may be enough.
- **P2 internal/shared behavior:** E2 plus owner or test confirmation.
- **P1 data/API/mobile/job compatibility:** E3 and/or E4 plus rollout or migration plan.
- **P0 auth, billing, privacy, deletion, security, or irreversible data mutation:** E4 + E5 + E6.

For detailed examples of each evidence level and confidence-mapping guidance, see `references/evidence_rubric.md`.

## Workflow

### 1. Scope the candidate

Create a candidate record:

```yaml
candidate_id: LSA-001
location: path/to/file.ts:123
legacy_contract: "Accepts old payload field `user_id` in addition to `userId`."
change_under_review: "Removes the `user_id` fallback."
risk_domain: api | database | frontend | mobile | job | config | build | model | security | unknown
known_owner: unknown
initial_concern: "Local references are gone, but old mobile clients may still send the field."
```

If the change matches multiple categories or the legacy contract is ambiguous, consult `references/legacy_patterns.yml` for the category taxonomy and the recommended `evidence_to_seek` list per category.

### 2. Recover history

Use history to understand why the path exists:

- `git blame <file>` around the compatibility branch.
- `git log -S '<legacy token>' -- <path>` to find introduction/removal commits.
- Search linked issues, PRs, incidents, release notes, migration docs, TODOs, and deprecation notices.
- Identify whether the path came from a migration, rollout, public API promise, customer request, incident, rollback requirement, import format, or temporary repair.

For a one-shot history pull on a token or file, run:

```bash
bash scripts/git_support_archaeology.sh <token-or-file> [path]
```

### 3. Trace consumers

Trace in this order:

1. Same function/file/package.
2. Same repository.
3. Adjacent repositories: web, mobile, backend, SDK, cron, analytics, infra, shared package.
4. Data stores: relational rows, JSON blobs, object keys, event payloads, queues, caches, local storage, backups.
5. Runtime systems: logs, traces, endpoint hits, metrics, feature flags, crash reports, support tickets.
6. Human/contracts: code owners, public docs, API lifecycle policy, customer commitments, release policy.

If a layer is unavailable, say exactly what was not checked.

### 4. Decide whether old inputs can still happen

Do not confuse "current writer no longer emits old shape" with "old reader can be removed." Ask:

- Are old clients still supported or installed?
- Are old events replayable?
- Can stale cached/session/local-storage values rehydrate?
- Can old files still be imported?
- Can rollback recreate the old producer?
- Do migrations need to run from older database states?
- Do backups/restores contain the old schema?
- Do delayed jobs, queues, or webhooks still carry old payloads?
- Is the path needed for support, privacy deletion, compliance, or account recovery?

Before finalizing a removal verdict, scan `examples/decision_traps.md` to rule out common false-removal patterns.

### 5. Classify risk

Use the highest applicable risk:

- **P0 Critical:** auth, payments, privacy, deletion, security, legal retention, account access, irreversible data mutation.
- **P1 High:** public API, mobile compatibility, customer integration, database migration, cross-repo shared package, background job, webhooks.
- **P2 Medium:** internal API, admin tool, analytics/reporting, import/export, feature flag cleanup, noncritical model fallback.
- **P3 Low:** test-only shim, local UI fallback, old copy, retired build option, internal script with owner confirmation.

For risk-to-evidence-minimum calibration, cross-reference `references/evidence_rubric.md`.

### 6. Choose a verdict

#### RETAIN

Use when the contract still exists. Recommend preserving tests, comments, docs, or owner metadata so future reviewers do not repeatedly rediscover the same reason.

#### DEPLOY OBSERVABILITY

Use when the path may be dead but runtime/data evidence is missing. Recommend a specific metric/log/event, observation window, success threshold, and follow-up removal ticket.

#### DEPRECATE

Use when consumers may still exist but the team wants to end support. Recommend migration steps, communication mechanism, deprecation signal, sunset/removal date, and temporary compatibility tests.

#### QUARANTINE

Use when the path is messy or risky but cannot be removed. Recommend moving it behind a named compatibility boundary with tests and clear removal criteria.

#### REMOVE

Use only when evidence shows the support contract no longer exists. Keep the removal focused, preserve regression tests for the canonical path, and include rollback notes for production-facing paths.

For worked examples of each verdict on realistic cases, see `examples/example_verdicts.md`.

## Output format

End every review with this block. For a copyable template with field hints, see `references/report_template.md`.

```markdown
### Legacy Support Adjudication Verdict

**Verdict:** REMOVE | RETAIN | DEPRECATE | QUARANTINE | DEPLOY OBSERVABILITY  
**Confidence:** High | Medium | Low  
**Risk:** P0 | P1 | P2 | P3  
**Legacy contract:** <specific old thing being supported>  
**Consumer reality:** <who still uses it, or what was checked>  
**Producer reality:** <whether current systems can still produce/receive it>  
**Evidence:**
- <static evidence>
- <data/runtime evidence>
- <owner/docs evidence>

**Required before merge:**
- <tests, instrumentation, migration, owner signoff, staged rollout, docs>

**Recommended cleanup path:**
- <concrete next action>
```

For drafting the actual review comment that accompanies the verdict, see `references/review_comment_templates.md` for under-evidenced-removal, safe-removal, quarantine-first, and deprecation-path templates.

## Hard rules

These apply on every adjudication, regardless of how confident the diff looks:

- Do not approve removal solely because local static search found no references.
- Do not assume current writers define all possible inputs.
- Do not treat missing telemetry as proof of zero usage.
- Do not remove migration history unless the project explicitly supports migration squashing/pruning.
- Do not remove public API, mobile, auth, billing, privacy, deletion, or data migration compatibility without a staged plan.
- If evidence is incomplete, lower confidence and recommend observability, quarantine, or deprecation.

## Optional: scan for candidates

When reviewing a large PR or auditing a repository, the bundled scanner produces candidate paths to adjudicate:

```bash
# Scan the whole tree, emit a markdown report:
python3 scripts/legacy_support_scan.py --root . --format markdown --output lsa-report.md

# Scan only files changed vs a base ref:
python3 scripts/legacy_support_scan.py --root . --changed-only --base origin/main --format json --output lsa.json

# Render the JSON output into a compact review-ready report:
python3 scripts/render_lsa_report.py lsa.json --top 25 --output lsa-review.md
```

The scanner produces E0 (suspicion-only) candidates. Each candidate still needs the full workflow above before any verdict.

For Semgrep-based scanning, see `semgrep/legacy-support-patterns.yml`.

## Bundled files

- `scripts/legacy_support_scan.py` — heuristic candidate scanner (stdlib only).
- `scripts/git_support_archaeology.sh` — git blame + `git log -S` helper.
- `scripts/render_lsa_report.py` — JSON to markdown report renderer.
- `references/evidence_rubric.md` — detailed evidence-level and confidence rubric.
- `references/legacy_patterns.yml` — pattern taxonomy and search vocabulary by category.
- `references/report_template.md` — copyable verdict-report skeleton.
- `references/review_comment_templates.md` — reusable PR-review comment templates.
- `examples/example_verdicts.md` — worked case studies with full verdict reasoning.
- `examples/decision_traps.md` — common false-removal patterns to rule out.
- `examples/agent_prompt.md` — prompt wrapper for review agents.
- `semgrep/legacy-support-patterns.yml` — starter Semgrep ruleset.
