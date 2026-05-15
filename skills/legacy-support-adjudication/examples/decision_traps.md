# Decision Traps for Legacy Support Adjudication

These are common situations where agents often overconfidently recommend removal.

## Trap 1 — Current writer is clean, old reader still needed

Current code may no longer write an old schema, but existing data, restored backups, imports, event replays, or local caches may still contain it.

**Do not say:** “The writer no longer emits this, so remove the reader.”  
**Ask instead:** “Can any persisted or replayed input still contain the old shape?”

Typical evidence needed: E3 data scan, fixture review, replay/retention policy.

## Trap 2 — Current UI is clean, public API is not

A web frontend search does not prove external clients, SDKs, mobile apps, scripts, or customer integrations stopped using an old API shape.

Typical evidence needed: E4 logs by client/source, E5 API-owner confirmation, docs/SDK scan.

## Trap 3 — Flag branch has zero normal traffic, but is still rollback

Feature flag off-branches can be operational dependencies even when product traffic is zero.

Typical evidence needed: flag dashboard, incident playbook, on-call owner signoff, replacement rollback strategy.

## Trap 4 — Old migration already ran in production

Old migrations may still be needed for fresh database bootstraps, preview apps, CI, new tenants, and auditability.

Typical evidence needed: bootstrap process check, migration-tooling behavior, squashed-baseline plan.

## Trap 5 — Tests pass, but tests do not model production history

Tests often cover the current happy path. They may omit old mobile clients, old database rows, replayed events, old local storage, or partner payloads.

Typical evidence needed: historical fixtures, data/runtime checks, contract docs.

## Trap 6 — Rare execution is not the same as dead code

Repair jobs, import parsers, fallback auth, payment lifecycle handlers, and disaster recovery code may execute rarely but still be critical.

Typical evidence needed: risk classification, invariant protected, last-execution logs, owner confirmation.

## Trap 7 — Removing support improves security but breaks customers

Security-sensitive legacy support may need constrained deprecation, not immediate removal.

Typical evidence needed: security owner signoff, allowlist, customer migration plan, staged disable.

## Trap 8 — Old package alias is safe internally but not externally

The same code can be removable in a controlled monorepo and not removable in a public SDK.

Typical evidence needed: package visibility, consumer inventory, semantic-versioning policy, release notes.

## Trap 9 — Local storage and deep links live outside deploy control

Browsers, emails, bookmarks, push notifications, QR codes, and user-shared links can preserve old formats after producers change.

Typical evidence needed: analytics, one-shot migrations, old template scan, source-specific link tracking.

## Trap 10 — Analytics/warehouse consumers are invisible to app search

SQL files, BI models, notebooks, scheduled exports, and reverse ETL can depend on legacy columns or enum values.

Typical evidence needed: warehouse query search, BI catalog search, scheduled job inventory, data-owner confirmation.
