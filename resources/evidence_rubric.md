# Evidence Rubric: Legacy Support Adjudication

## Evidence levels

### E0 — Suspicion only
Examples: `legacy`, `TODO remove`, `v1`, stale comments, old branch names, deleted feature references.

Use E0 only to trigger investigation. It cannot justify removal.

### E1 — Local static evidence
Examples: grep/AST search shows no direct references in the edited package; tests pass after deleting branch locally.

Good for small internal helpers. Weak for APIs, data, clients, jobs, and generated/runtime references.

### E2 — Cross-boundary static evidence
Examples: no references in API specs, SDKs, generated clients, frontend, mobile, cron jobs, configs, infra, shared packages.

Useful for monorepos and tightly controlled systems. Still incomplete if dynamic data or external clients exist.

### E3 — Data evidence
Examples: production query shows zero rows with old field/state; object storage sample has no old files; queue/event payload scan has no legacy shape; cache/local storage migration is complete.

Required for schema, payload, import/export, migration, and persisted-state compatibility.

### E4 — Runtime evidence
Examples: access logs show zero hits for old endpoint/version over a representative period; feature flag exposures are zero; error monitoring shows no old-client fallbacks; traces show no branch execution.

Required for public APIs, mobile, external integrations, background jobs, and service boundaries.

### E5 — Contract/owner evidence
Examples: API policy permits removal; owner confirms no supported consumers; release notes announced deprecation; customer/integration owners migrated; support docs updated.

Required when compatibility is a promise to humans or external systems.

### E6 — Staged validation
Examples: dark-disable, canary, shadow removal, dry-run migration, kill-switch, rollback test, progressive deploy with alerting.

Required for high-risk or irreversible paths.

## Recommended minimum by risk

| Risk | Examples | Minimum before REMOVE |
|---|---|---|
| P0 Critical | auth, billing, privacy, deletion, security, irreversible mutation | E3/E4 + E5 + E6 + rollback/incident plan |
| P1 High | public API, mobile, DB migration, background jobs, customer integrations | E2 + E3/E4 + E5; E6 if production-facing |
| P2 Medium | internal API, admin, analytics, imports/exports, feature flags | E2 + E3 or E4 depending on boundary |
| P3 Low | local UI fallback, test-only shim, retired build target | E1 + tests; owner confirmation if unclear |

## Confidence mapping

- **High confidence:** Evidence meets or exceeds risk minimum; missing layers are explicitly irrelevant.
- **Medium confidence:** Evidence is mostly adequate, but one layer is sampled, indirect, or owner-dependent.
- **Low confidence:** Static evidence only; runtime/data/contract layers unknown; dynamic consumers possible.

## Decision guide

- If evidence is weak but the code is contained: **QUARANTINE**.
- If evidence is weak and runtime use is plausible: **DEPLOY OBSERVABILITY**.
- If consumers exist but should move: **DEPRECATE**.
- If consumers exist and must remain: **RETAIN**.
- If contract is dead and risk is controlled: **REMOVE**.
