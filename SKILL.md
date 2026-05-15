# Legacy Support Adjudication Skill

## Purpose

Use this skill during code review when a change touches backward-compatibility logic, migration shims, old schema handling, transitional formats, feature-flag fallbacks, deprecated API versions, old client behavior, data import/export compatibility, or build/runtime support for retired environments.

This skill does **not** merely ask whether code is reachable. It asks whether the historical support contract is still real.

The expected output is a verdict with evidence, confidence, risk, and a concrete next action:

- **RETAIN** — still required; preserve or strengthen tests/docs.
- **DEPLOY OBSERVABILITY** — not enough evidence; instrument before deciding.
- **DEPRECATE** — still possibly used; start a formal migration/removal path.
- **QUARANTINE** — isolate behind a named compatibility boundary while evidence is gathered.
- **REMOVE** — support contract no longer exists; remove with safeguards.

## When to invoke

Invoke this skill when you see any of the following in a diff, issue, or review request:

- Branches named `legacy`, `compat`, `backcompat`, `fallback`, `old`, `v1`, `deprecated`, `migration`, `shim`, `transitional`, `adapter`, `normalize`, `upgrade`, `downgrade`, or `TODO remove`.
- Code that accepts multiple schema shapes, API versions, enum names, payload formats, field names, storage layouts, client versions, auth formats, or protocol variants.
- Database migrations that preserve old columns/tables, dual-write/dual-read logic, shadow fields, nullable historical fields, backfill scripts, or data repair jobs.
- Frontend/mobile code that normalizes historical server responses, handles old app versions, reads stale local storage keys, or supports old deep links.
- CI/build/deployment logic for old runtimes, old package managers, old operating systems, retired browsers, retired environments, or old toolchains.
- Any reviewer comment like “can we delete this yet?”, “is this still needed?”, “old clients?”, “migration complete?”, or “probably dead code.”

## Core questions

For every candidate legacy path, answer these five questions:

1. **What old thing is being supported?**  
   Identify the exact contract: old endpoint, old response shape, old DB schema, old enum, old feature flag state, old client version, old config, old job, old import/export format, old auth/session format, etc.

2. **Who still uses it?**  
   Trace actual consumers across code, data, clients, deployments, jobs, queues, configs, docs, tests, support scripts, analytics, and operational dashboards.

3. **Can new inputs still produce it?**  
   Determine whether current systems can still create, receive, hydrate, import, sync, cache, or replay the legacy shape.

4. **What breaks if it disappears?**  
   Identify runtime failures, data loss, migration gaps, API breakage, user-visible regressions, failed background jobs, rollback risks, and support obligations.

5. **What evidence is strong enough to remove it?**  
   Require evidence appropriate to the risk level: static proof, runtime telemetry, data scans, owner confirmation, staged disable, tests, rollout plan, and rollback plan.

## Evidence hierarchy

Use the strongest evidence available. Do not treat weaker evidence as proof.

| Level | Evidence type | Meaning | Typical use |
|---|---|---|---|
| E0 | Suspicion only | Keyword/comment/history suggests legacy support | Start investigation only |
| E1 | Local static references | Search/AST shows no direct references in current repo | Useful but never sufficient for cross-repo/client/data paths |
| E2 | Cross-boundary static references | API specs, shared packages, clients, jobs, configs, generated code, tests checked | Good for internal-only code |
| E3 | Data reality | DB/table scans, object storage samples, queues, events, local storage keys, cached payloads checked | Needed for schema/format support |
| E4 | Runtime reality | Logs, traces, analytics, access records, feature flag exposure, endpoint hits over a representative window | Needed for public/production-facing paths |
| E5 | Human/contract confirmation | Owner, API policy, support policy, deprecation notice, customer/client confirmation | Needed when contracts are external or ambiguous |
| E6 | Staged validation | dark-disable, shadow removal, canary, kill switch, rollback tested | Strongest removal proof for high-risk paths |

Minimum evidence standard:

- Low-risk internal fallback: E1 + tests may be enough.
- Shared package or internal API: E2 + owner confirmation.
- DB/data compatibility: E3 + migration/backfill proof + rollback plan.
- Public API/mobile/client compatibility: E4 + E5 + staged rollout.
- Auth, billing, compliance, deletion, privacy, security, or data-loss path: E4 + E5 + E6.

## Review workflow

### 1. Scope the candidate

Create a candidate record for each legacy path:

```yaml
candidate_id: LSA-001
location: path/to/file.ts:123
legacy_contract: "Accepts old payload field `user_id` in addition to `userId`."
current_change: "PR removes the `user_id` fallback."
owner: unknown
risk_domain: api | database | frontend | mobile | job | config | build | model | security | unknown
initial_verdict: investigate
```

### 2. Recover history

Use repository history to understand why the support was introduced:

- `git blame <file>` around the branch/shim.
- `git log -S '<legacy_token>' -- <file>` to find introduction/removal commits.
- Search linked issues, PR titles, migration docs, release notes, incidents, and TODOs.
- Check whether the compatibility path was tied to a specific migration, launch, customer, release, rollback, data import, or incident.

Do not assume that “old” means “safe to delete.” Old support code often exists because an external contract outlived the original implementation.

### 3. Trace consumers

Trace consumers in this order:

1. **Same file and same package** — direct calls, branches, tests, types, fixtures.
2. **Same repository** — imports, route definitions, schema validators, generated code, config, env vars, scripts.
3. **Adjacent repositories** — frontend, mobile, backend, cron, analytics, infra, SDKs, shared packages.
4. **Data stores** — columns, JSON fields, object keys, event payloads, queue messages, cache entries, local storage.
5. **Runtime systems** — logs, traces, endpoint hits, feature flag exposures, error reports, metrics.
6. **Humans/contracts** — owners, release docs, API policies, migration guides, customer support constraints.

If you cannot inspect a layer, say so explicitly and lower confidence.

### 4. Decide whether new legacy inputs are still possible

Ask whether current production can still create or receive the old shape:

- Are old clients still accepted?
- Are old app versions still active?
- Can old events be replayed from queues or logs?
- Can old files be imported?
- Can stale local storage/session/cache values rehydrate?
- Can rollback resurrect the old producer?
- Can batch jobs, cron tasks, or third-party integrations still send it?
- Does the DB still contain rows requiring this path?
- Does test data or seed data incorrectly keep the path alive?

A path is not removable merely because the current writer no longer emits the old format.

### 5. Classify risk

Use the highest applicable risk class:

- **P0 Critical:** auth, payments, privacy, security, legal retention, account access, irreversible data mutation/deletion.
- **P1 High:** public API, mobile app compatibility, database schema migration, background jobs, customer integrations, cross-repo shared package.
- **P2 Medium:** internal API, admin tool, analytics/reporting, import/export, feature flag cleanup.
- **P3 Low:** local UI fallback, test-only shim, old copy, retired build option, internal script with owner confirmation.

### 6. Produce a verdict

Use one of these verdicts:

#### RETAIN
Use when the support contract still exists or evidence is too weak for removal but the path is clearly intentional.

Required output:

- What depends on it.
- What tests/docs should preserve it.
- Who owns the contract.
- Whether it should be renamed/commented for clarity.

#### DEPLOY OBSERVABILITY
Use when the path may be removable but runtime/data evidence is missing.

Required output:

- What metric/log/event should be added.
- Suggested observation window.
- Expected threshold for removal.
- Where the follow-up ticket should point.

#### DEPRECATE
Use when consumers still exist or may exist, but the team wants to end the contract.

Required output:

- Consumer migration path.
- Communication mechanism.
- Deprecation date and sunset/removal date if applicable.
- Compatibility tests to keep until sunset.

#### QUARANTINE
Use when the path is messy or risky but cannot be removed now.

Required output:

- Compatibility boundary name.
- File/module where legacy logic should live.
- Tests that lock current behavior.
- Removal criteria.

#### REMOVE
Use only when evidence shows the support contract no longer exists.

Required output:

- Evidence summary.
- Risk classification.
- Required tests.
- Rollout/rollback note if production-facing.
- Follow-up cleanup list.

## Output format

Every review should end with this block:

```markdown
### Legacy Support Adjudication Verdict

**Verdict:** REMOVE | RETAIN | DEPRECATE | QUARANTINE | DEPLOY OBSERVABILITY  
**Confidence:** High | Medium | Low  
**Risk:** P0 | P1 | P2 | P3  
**Legacy contract:** <specific old thing being supported>  
**Consumer reality:** <who still uses it, or what was checked>  
**Producer reality:** <whether current systems can still produce/receive it>  
**Evidence:**
- <file/static evidence>
- <data/runtime evidence>
- <owner/docs evidence>

**Required before merge:**
- <tests, instrumentation, migration, owner signoff, staged rollout, docs>

**Recommended cleanup path:**
- <concrete next action>
```

## Review comment templates

### Removal is under-evidenced

> I would not remove this yet. This looks like compatibility logic rather than simple dead code. Before deletion, please identify the legacy contract it supports, check whether any current clients/data/jobs can still produce that shape, and add evidence from runtime logs or data scans if this crosses a repo/API/database boundary.

### Removal looks safe

> This looks removable based on the evidence: no static consumers, current producers no longer emit the old shape, and runtime/data checks show no usage over the relevant window. Please keep the removal small, add/adjust regression tests around the new canonical path, and include a rollback note if this is production-facing.

### Quarantine instead of deletion

> I agree this legacy path is technical debt, but the support contract is not proven dead. I recommend moving it behind a named compatibility boundary with tests and adding instrumentation. That gives us a safe path to remove it later without spreading the shim further.

### Add deprecation path

> This should probably become a deprecation rather than an immediate removal. The PR should define the replacement behavior, identify known consumers, add deprecation signaling where appropriate, and create a dated removal criterion.

## Common false positives

Do not flag these as removable without additional evidence:

- Historical migrations that must remain for fresh environment bootstraps.
- Rollback paths needed during deploys.
- Old schema readers needed for restored backups or delayed jobs.
- API fallbacks used by mobile versions still in the wild.
- Test fixtures representing real historical production data.
- Importers for files users can still upload.
- Admin/support scripts run rarely but intentionally.
- Feature flag “off” branches still needed for safe rollback.
- Data privacy/deletion code for old account states.
- Build scripts for release branches still maintained.

## Hard rules

- Do not approve removal solely because local static search found no references.
- Do not assume current writers define all possible inputs.
- Do not treat missing telemetry as proof of zero usage.
- Do not remove migration history unless the project’s migration strategy explicitly allows squashing/pruning.
- Do not remove compatibility paths from public APIs, mobile contracts, auth, billing, privacy, deletion, or migrations without a staged plan.
- If evidence is incomplete, lower confidence and recommend observability or quarantine.

## Optional tools

This skill package includes:

- `scripts/legacy_support_scan.py` — repository scanner for compatibility-debt signals.
- `scripts/git_support_archaeology.sh` — quick git-history helper for a token or file.
- `scripts/render_lsa_report.py` — converts scanner JSON into a review-ready markdown report.
- `resources/legacy_patterns.yml` — pattern inventory for agents and scanners.
- `resources/evidence_rubric.md` — detailed evidence thresholds.
- `resources/report_template.md` — copyable verdict template.
- `semgrep/legacy-support-patterns.yml` — starter Semgrep rules.

## Agent behavior guidance

When using this skill as a code-review agent:

1. Be skeptical but not obstructionist.
2. Prefer small, reversible cleanup PRs over broad refactors.
3. Separate “this is ugly” from “this support contract is dead.”
4. Ask for exactly the missing evidence needed for the risk level.
5. Preserve momentum: when deletion is not yet safe, recommend observability, quarantine, or a dated deprecation plan.
6. Be explicit about uncertainty.
7. Never invent runtime evidence. If logs/data/owners were not checked, say that.
