# Example Verdicts and Complex Case Studies

These examples are intentionally more nuanced than ordinary dead-code examples. Each case focuses on a compatibility contract: an old behavior, old format, old client, old data shape, old operational path, or old integration that may still have real consumers.

Use these examples as patterns for code-review agents. The exact verdict is less important than the reasoning standard: identify the contract, trace consumers and producers, name unchecked layers, then choose the safest cleanup path.

## Reading guide

A good verdict should not say only “unused” or “used.” It should answer:

1. What old thing is being supported?
2. Who can still consume or produce it?
3. What evidence was checked?
4. What evidence is missing?
5. What action is safe now?

---

## Example 1 — API field alias with unknown mobile clients

### Situation

A backend endpoint accepts both `userId` and the older `user_id` request field. A PR removes the alias because the current web frontend sends only `userId`.

### Nuance

This is not local dead code. Request payloads may come from mobile apps, SDKs, third-party integrations, scripts, retries, old clients, or customer-owned systems. Static search in the web repo is weak evidence.

### Legacy Support Adjudication Verdict

**Verdict:** DEPLOY OBSERVABILITY  
**Confidence:** Low  
**Risk:** P1  
**Legacy contract:** Backend accepts `user_id` in addition to canonical `userId`.  
**Consumer reality:** Static repo search shows no current web client sends `user_id`, but mobile clients, SDKs, third-party integrations, support scripts, and raw API callers were not checked.  
**Producer reality:** Current web producer emits only `userId`; old mobile versions or integration clients may still emit `user_id`.

**Evidence:**

- Local web repo contains no active references to `user_id`.
- Backend tests include a fixture for `user_id`, but the fixture does not say whether it represents production traffic.
- No access-log, client-version, or API-key-level evidence was included.

**Required before merge:**

- Add temporary metric/log for requests where `user_id` is present.
- Break down usage by client version, API key, user agent, or integration source if available.
- Check public API docs and SDKs for mention of `user_id`.
- Define an observation window appropriate to release cadence, usually 30–90 days for mobile/public API compatibility.

**Recommended cleanup path:**

- Quarantine alias handling in a named compatibility module such as `legacyPayloadAliases.ts`.
- If usage is zero after the observation window and owners confirm no external contract, remove the alias in a small PR with regression tests for the canonical field.

### Why not REMOVE?

The only evidence is local static search. That does not cover external payload producers.

---

## Example 2 — Database fallback after completed backfill

### Situation

A reader falls back from `profile.display_name` to old nullable `profile.name`. The team believes a migration completed months ago.

### Nuance

For database compatibility, the decisive question is not just “do writers still write the old field?” It is also “does persisted data still require the fallback?”

### Legacy Support Adjudication Verdict

**Verdict:** REMOVE  
**Confidence:** High  
**Risk:** P1  
**Legacy contract:** Reader supports rows where `display_name` is missing but legacy `name` exists.  
**Consumer reality:** API responses and internal consumers now read only the canonical `display_name`.  
**Producer reality:** Writers stopped writing `name` in migration `2024-03-18-add-display-name`; production scans show no legacy-only rows.

**Evidence:**

- Migration backfilled `display_name` from `name` and updated writers to the canonical column.
- Production-safe query returned zero rows matching `display_name IS NULL AND name IS NOT NULL`.
- Insert/update code paths no longer write `name`.
- API tests cover canonical `display_name` behavior.

**Required before merge:**

- Add a guard, constraint, or test preventing new legacy-only rows.
- Keep rollback note for one release because the old reader is being removed before the old column is dropped.

**Recommended cleanup path:**

- Remove the fallback reader now.
- Drop the old column in a separate migration after one release cycle, once rollback no longer needs it.

### Why not drop the column in the same PR?

Reader removal and schema deletion have different rollback risks. Splitting them reduces blast radius.

---

## Example 3 — Feature flag off-branch used only for emergency rollback

### Situation

A recommendation system has a flag `new_recs_enabled`. Production has been at 100% enabled for 60 days. A PR deletes the old algorithm branch.

### Nuance

A branch with zero normal traffic may still be an operational rollback mechanism. Removing it without replacing the rollback path can increase incident risk.

### Legacy Support Adjudication Verdict

**Verdict:** QUARANTINE  
**Confidence:** Medium  
**Risk:** P2  
**Legacy contract:** Old recommendation algorithm remains available when `new_recs_enabled=false`.  
**Consumer reality:** Normal production users no longer receive the old algorithm, but the incident playbook still names the flag as an emergency fallback.  
**Producer reality:** Current requests can still execute the old path if the flag is flipped.

**Evidence:**

- Feature flag dashboard shows 100% exposure to the new algorithm in production.
- Staging and rollback playbooks still reference the old branch.
- No evidence was provided that a new rollback strategy exists.

**Required before merge:**

- Move old algorithm into a named module such as `legacy/recsFallback.ts`.
- Add an alert if the old branch executes in production.
- Update the incident playbook with a replacement rollback strategy.
- Create a removal ticket with an owner and deadline.

**Recommended cleanup path:**

- Do not delete immediately.
- Quarantine now, then remove once rollback documentation and on-call owners no longer depend on it.

### Why not RETAIN forever?

The path is not part of product behavior anymore. It should not remain scattered through normal code. Quarantine makes the debt visible and bounded.

---

## Example 4 — Mobile app response normalizer for old backend payloads

### Situation

The iOS app normalizes server responses that may contain `avatar_url`, `avatarUrl`, or `profileImage`. The backend now returns only `avatarUrl`. A PR removes the normalizer from the mobile app.

### Nuance

Mobile apps are both consumers and caches. Even if the server is clean, old payloads may still exist in local persistence, offline queues, app extensions, push notification payloads, or restored backups.

### Legacy Support Adjudication Verdict

**Verdict:** DEPLOY OBSERVABILITY  
**Confidence:** Medium-Low  
**Risk:** P1  
**Legacy contract:** Mobile client can hydrate old cached profile payloads with `avatar_url` or `profileImage`.  
**Consumer reality:** Current API no longer sends old fields, but installed app versions and local caches were not fully checked.  
**Producer reality:** Server no longer emits old fields; persisted local data and push payload archives may still contain them.

**Evidence:**

- Backend OpenAPI schema and current server code expose only `avatarUrl`.
- iOS code has a local database migration that claims to rewrite `avatar_url`, but it is not tested against restored backup state.
- Crash logs do not show clear failures, but no metric tracks legacy field hydration.

**Required before merge:**

- Add migration tests using archived local database fixtures from older app versions.
- Check minimum supported app version and active-version distribution.
- Add telemetry for legacy field hydration, at least for one release.
- Confirm push payloads and notification extensions do not use the old names.

**Recommended cleanup path:**

- Keep the normalizer for one more mobile release, but isolate it as `LegacyProfilePayloadNormalizer`.
- Remove only after telemetry shows zero legacy hydration and active old versions fall below the team’s threshold.

### Why this is tricky

The backend producer may be fixed while the mobile client still has to read historical data on disk.

---

## Example 5 — API v1 route with no current web references but external contract

### Situation

A PR removes `/api/v1/orders/:id` because the current frontend uses `/api/v2/orders/:id`.

### Nuance

Versioned public endpoints are contracts. Their removability depends on API lifecycle policy, external traffic, SDK support, documentation, and communicated sunset dates.

### Legacy Support Adjudication Verdict

**Verdict:** DEPRECATE  
**Confidence:** Medium  
**Risk:** P1  
**Legacy contract:** Public API v1 order lookup remains available for external clients.  
**Consumer reality:** Internal web and mobile clients use v2, but access logs show low but nonzero v1 traffic from two API keys.  
**Producer reality:** External clients can still call v1 directly.

**Evidence:**

- OpenAPI v2 spec is canonical for internal clients.
- Access logs show v1 endpoint traffic in the last 14 days.
- API docs still list v1 as supported.
- No deprecation or sunset notice is linked from the PR.

**Required before merge:**

- Do not remove v1 in this PR.
- Add deprecation signaling, migration documentation, and owner-approved removal timeline.
- Contact or identify the two API-key owners.
- Add tests that keep v1 stable until sunset.

**Recommended cleanup path:**

- Mark v1 deprecated now.
- Set a removal date according to API policy.
- Remove only after traffic reaches the agreed threshold and the deprecation window has elapsed.

### Why not DEPLOY OBSERVABILITY?

There is already evidence of active use. This needs a deprecation program, not merely more metrics.

---

## Example 6 — Dual-write during database migration where read path looks unused

### Situation

A service writes to both `orders.status` and `orders.status_v2`. The read path uses only `status_v2`. A PR removes writes to `status`.

### Nuance

Dual-write cleanup requires checking readers outside the service, downstream ETL, analytics jobs, customer exports, backfills, and rollback migrations. The field can be unused in application reads but still used by batch systems.

### Legacy Support Adjudication Verdict

**Verdict:** QUARANTINE  
**Confidence:** Medium  
**Risk:** P1  
**Legacy contract:** `orders.status` remains populated for older readers and downstream jobs during migration to `status_v2`.  
**Consumer reality:** Online service reads no longer use `status`, but nightly revenue export still selects it.  
**Producer reality:** Current writes still populate both columns; if legacy write stops, downstream export may silently degrade.

**Evidence:**

- Application code reads `status_v2` only.
- SQL search found `orders.status` in `revenue_export.sql` and one BI model.
- Migration docs say `status` removal is phase 4, but current PR is phase 2.

**Required before merge:**

- Do not remove legacy write until downstream jobs migrate.
- Add a named migration phase checklist.
- Update export/BI owners.
- Consider adding a validation query that compares `status` and `status_v2` until removal.

**Recommended cleanup path:**

- Quarantine dual-write logic in `OrderStatusMigrationCompat`.
- Remove once downstream dependencies are migrated and a production data comparison shows parity.

### Why this matters

Online code search can miss SQL files, BI models, notebook jobs, and warehouse consumers.

---

## Example 7 — Event consumer supports old schema because replay is possible

### Situation

An event consumer handles both `UserSignedUpV1` and `UserSignedUpV2`. All current producers emit V2. A PR removes V1 handling.

### Nuance

Event systems preserve history. Old events can reappear through replay, dead-letter queue reprocessing, backfills, disaster recovery, or regional replication delays.

### Legacy Support Adjudication Verdict

**Verdict:** RETAIN  
**Confidence:** High  
**Risk:** P1  
**Legacy contract:** Consumer can process historical `UserSignedUpV1` events.  
**Consumer reality:** The consumer still receives V1 during replay and DLQ reprocessing.  
**Producer reality:** New production emits V2, but old V1 events exist in retention and can be replayed.

**Evidence:**

- Event catalog says `UserSignedUpV1` is retained for 13 months.
- Replay tooling does not transform V1 to V2 before delivery.
- DLQ contains recent V1 events from a replay job.
- Consumer tests include a V1 fixture from production history.

**Required before merge:**

- Keep V1 handler.
- Add clear comments documenting that the path is replay compatibility, not active producer compatibility.
- Add metric for V1 processing volume.

**Recommended cleanup path:**

- Revisit after event retention expires or after replay tooling guarantees V1-to-V2 transformation.

### Why not REMOVE?

Current producers are not the only source of events. Historical replay is a valid producer.

---

## Example 8 — Frontend localStorage key migration

### Situation

A React app reads both `pm_theme` and old `themePreference` from `localStorage`. A PR removes the old key reader because the migration shipped six months ago.

### Nuance

Local storage migrations depend on whether users have opened the app since the migration shipped. Infrequent users can skip the migration window and return later with old state.

### Legacy Support Adjudication Verdict

**Verdict:** DEPRECATE  
**Confidence:** Medium  
**Risk:** P2  
**Legacy contract:** Frontend reads old `themePreference` localStorage key and migrates it to `pm_theme`.  
**Consumer reality:** Active users likely migrated, but dormant users may still have the old key.  
**Producer reality:** Current app writes only `pm_theme`; browsers with old local storage can still present `themePreference`.

**Evidence:**

- Current app writes only `pm_theme`.
- Migration shipped six months ago.
- No runtime metric tracks old-key reads.
- Removing fallback would likely reset a preference, not break account access or data integrity.

**Required before merge:**

- Add a final migration path that reads old key once, writes canonical key, then deletes old key.
- Add a test for a dormant-user localStorage fixture.
- Optionally log non-identifying migration count for one release.

**Recommended cleanup path:**

- Keep one-shot migration for one additional release.
- Remove old-key reader after migration telemetry shows near-zero usage or after the team accepts the low UX risk.

### Why not just REMOVE?

The risk is not severe, but the cost of a one-shot migration is low and avoids unnecessary preference resets.

---

## Example 9 — Auth session compatibility for old token claims

### Situation

Authentication middleware accepts both `sub` and older `user_id` claims in JWT/session tokens. Current auth service issues only `sub`. A PR removes `user_id` support.

### Nuance

Auth compatibility is P0/P1 depending on product context. Old tokens may remain valid until expiry, long-lived refresh tokens may mint sessions, and rollback can reintroduce old claims.

### Legacy Support Adjudication Verdict

**Verdict:** DEPLOY OBSERVABILITY  
**Confidence:** Low  
**Risk:** P0  
**Legacy contract:** Middleware authenticates sessions where identity is encoded as `user_id` instead of standard `sub`.  
**Consumer reality:** Current auth service emits `sub`, but existing valid sessions, refresh tokens, SSO integrations, and service tokens were not checked.  
**Producer reality:** New normal login emits `sub`; long-lived or external token issuers may still produce `user_id`.

**Evidence:**

- Current auth code issues `sub`.
- Unit tests still include `user_id` token fixtures.
- No token-claim usage logs or expiration analysis included.
- No SSO/service-token owner confirmation included.

**Required before merge:**

- Do not remove in this PR.
- Add safe instrumentation for legacy-claim authentication without logging secrets.
- Check token TTLs, refresh-token behavior, service accounts, and SSO integrations.
- Create a staged disable plan with a kill switch and rollback.

**Recommended cleanup path:**

- Remove only after legacy-claim usage is zero over at least the maximum relevant token lifetime and all token issuers are confirmed canonical.

### Why this is high stakes

A wrong removal can lock users or services out. Static proof is not enough for auth/session compatibility.

---

## Example 10 — Import parser for historical CSV exports

### Situation

An admin import tool accepts an old CSV header `Full Name` and new header `display_name`. A PR removes the old header parser because the export tool now emits `display_name`.

### Nuance

Import compatibility is often about files that already exist outside the system. The old producer may be gone, but old artifacts may remain valid inputs.

### Legacy Support Adjudication Verdict

**Verdict:** RETAIN  
**Confidence:** Medium  
**Risk:** P2  
**Legacy contract:** Admin import supports historical CSV files with `Full Name` header.  
**Consumer reality:** Support team still imports old customer files during migrations.  
**Producer reality:** New exports use `display_name`, but historical files can still be uploaded.

**Evidence:**

- Export code no longer emits `Full Name`.
- Support docs include old migration instructions using the historical CSV template.
- Recent support ticket references importing a customer’s old CSV.
- No replacement conversion tool exists.

**Required before merge:**

- Keep parser or provide a conversion tool.
- Document accepted legacy import formats.
- Add tests using archived historical CSV fixtures.

**Recommended cleanup path:**

- Retain until support confirms old imports are no longer accepted, or replace with an explicit offline conversion command.

### Why not DEPRECATE immediately?

If support still relies on old files, removal creates operational pain even though the current export path is clean.

---

## Example 11 — Build support for old Node version

### Situation

CI runs tests on Node 18 and Node 20. `package.json` says Node 20 is required. A PR removes Node 18 support and old polyfills.

### Nuance

Runtime and build support may be different. Local developer machines, deployment images, GitHub Actions, serverless functions, and package consumers may still use older versions even if `package.json` changed.

### Legacy Support Adjudication Verdict

**Verdict:** REMOVE  
**Confidence:** Medium-High  
**Risk:** P3  
**Legacy contract:** Package and CI support Node 18 runtime behavior.  
**Consumer reality:** Internal deployment and CI use Node 20; package is private and not externally consumed.  
**Producer reality:** No supported environment should run Node 18 after base-image migration.

**Evidence:**

- `engines.node` requires Node 20.
- Docker base image and deployment config use Node 20.
- CI matrix has included Node 18 only as a leftover from an older migration.
- Internal package registry shows no external consumers.

**Required before merge:**

- Remove Node 18 from CI matrix.
- Delete Node 18-specific polyfills in the same cleanup PR if tests pass.
- Update developer setup docs.

**Recommended cleanup path:**

- Remove now, because the support contract is internal, low-risk, and environment evidence is adequate.

### What would change the verdict?

If this were a public package or SDK, consumer-version evidence and deprecation policy would be required.

---

## Example 12 — Server accepts old enum value that maps to a new canonical state

### Situation

The backend maps old enum `PENDING_REVIEW` to new enum `AWAITING_REVIEW`. A PR removes the old enum value because no current UI exposes it.

### Nuance

Enums often persist in databases, queues, exports, analytics, partner webhooks, and archived objects. Removing an enum alias can break deserialization before business logic even runs.

### Legacy Support Adjudication Verdict

**Verdict:** DEPLOY OBSERVABILITY  
**Confidence:** Medium  
**Risk:** P1  
**Legacy contract:** System accepts and normalizes historical enum value `PENDING_REVIEW`.  
**Consumer reality:** Current UI does not send it; unknown whether DB rows, webhooks, or import jobs still contain it.  
**Producer reality:** Current UI produces only `AWAITING_REVIEW`, but external webhook senders and historical persisted data may still produce `PENDING_REVIEW`.

**Evidence:**

- Frontend search shows no references to `PENDING_REVIEW`.
- Backend enum normalizer still has tests for `PENDING_REVIEW`.
- No DB scan, webhook log check, or import sample check included.

**Required before merge:**

- Scan persisted data for `PENDING_REVIEW`.
- Check inbound webhook logs and import files.
- Add metric for normalization hits.
- If hits are zero and no external docs mention the old enum, schedule removal.

**Recommended cleanup path:**

- Keep the alias temporarily, but add observability and a removal criterion.

### Why this is not just frontend cleanup

A UI may stop producing an enum long before every database row or external sender stops containing it.

---

## Example 13 — Model-serving fallback for old feature vector

### Situation

A model server accepts both a 32-feature vector and an older 28-feature vector. The current online feature pipeline emits 32 features. A PR deletes the 28-feature adapter.

### Nuance

ML compatibility can include offline backfills, batch inference, notebooks, training data regeneration, shadow evaluation, and emergency model rollback. “Current online path” may not cover all producers.

### Legacy Support Adjudication Verdict

**Verdict:** QUARANTINE  
**Confidence:** Medium  
**Risk:** P2  
**Legacy contract:** Model server adapts historical 28-feature vectors to the current inference schema.  
**Consumer reality:** Online inference emits 32 features, but batch scoring and model evaluation notebooks still reference 28-feature fixtures.  
**Producer reality:** New online features are canonical; offline historical datasets can still produce 28-feature vectors.

**Evidence:**

- Online feature pipeline emits 32-feature payloads.
- Batch scoring script contains a compatibility call for 28-feature vectors.
- No owner confirmed that old datasets are no longer used for evaluation.

**Required before merge:**

- Move the adapter to `legacyFeatureVectorAdapter` with tests.
- Add warnings or metrics when 28-feature vectors are processed.
- Confirm whether batch/offline workflows still need historical scoring.

**Recommended cleanup path:**

- Quarantine now.
- Remove only after batch and evaluation workflows migrate or after old datasets are converted.

### Why this matters

ML systems often have production and offline consumers with different lifecycles.

---

## Example 14 — Webhook signature fallback for old secret format

### Situation

A webhook receiver verifies signatures using a new secret store, but also falls back to old per-customer secrets from a deprecated config table. A PR removes the fallback.

### Nuance

Webhook signature compatibility touches security and external integrations. Removing a fallback can break customers, but retaining it may create security exposure. The right answer may be deprecation with a narrow allowlist.

### Legacy Support Adjudication Verdict

**Verdict:** DEPRECATE  
**Confidence:** Medium  
**Risk:** P0  
**Legacy contract:** Webhook receiver accepts signatures generated with old per-customer secrets.  
**Consumer reality:** Logs show three customers still verifying through the old secret path.  
**Producer reality:** New integrations use the new secret store; existing external senders may still sign with old secrets.

**Evidence:**

- Signature verification metric shows nonzero old-secret fallback usage.
- Config table still contains active old secrets for three customers.
- No customer migration confirmation is included.
- Security review says fallback should be removed or tightly scoped.

**Required before merge:**

- Do not remove globally.
- Create customer-specific migration plan.
- Add allowlist and alerting so old-secret verification cannot expand.
- Set a sunset date with customer communication.
- Have security owner sign off.

**Recommended cleanup path:**

- Deprecate and constrain the fallback now.
- Remove after all customers rotate secrets and runtime fallback usage is zero.

### Why this is especially nuanced

Both retention and removal carry risk. The verdict must balance compatibility and security, not blindly preserve legacy behavior.

---

## Example 15 — Migration file looks old but is required for fresh installs

### Situation

A developer wants to delete old migration files because production has already run them and the schema is up to date.

### Nuance

Old migrations may be needed to build fresh development, test, staging, preview, or tenant databases from scratch. They may also serve as audit history.

### Legacy Support Adjudication Verdict

**Verdict:** RETAIN  
**Confidence:** High  
**Risk:** P1  
**Legacy contract:** Migration chain can create the database schema from an empty database.  
**Consumer reality:** Fresh environments, CI databases, preview apps, and new tenants rely on the full migration history.  
**Producer reality:** Any new database bootstrap still executes the historical migration chain.

**Evidence:**

- CI creates databases from scratch by running all migrations.
- Preview environments run migration chain on creation.
- No squashed baseline migration exists.
- Migration tooling expects all prior migration IDs to remain present.

**Required before merge:**

- Do not delete old migrations directly.
- If the team wants cleanup, create a formal squashed baseline migration and document cutover steps.
- Verify fresh bootstrap, rollback, and tenant creation after squashing.

**Recommended cleanup path:**

- Retain current migrations until a migration-squash process exists.

### Why not REMOVE?

“Already applied in production” does not mean “not needed.” Fresh environment creation is a real consumer.

---

## Example 16 — Legacy GraphQL field with generated clients

### Situation

A GraphQL schema includes deprecated field `fullName`; the canonical field is `displayName`. A PR removes `fullName` because no resolver code calls it internally.

### Nuance

GraphQL fields are consumed by generated clients, mobile apps, fragments, persisted queries, analytics dashboards, and third-party clients. Internal server usage is irrelevant.

### Legacy Support Adjudication Verdict

**Verdict:** DEPRECATE  
**Confidence:** Medium  
**Risk:** P1  
**Legacy contract:** GraphQL schema exposes deprecated field `User.fullName`.  
**Consumer reality:** Server code does not call `fullName`, but persisted query registry shows the field in 0.8% of recent requests.  
**Producer reality:** Clients can still query `fullName` as long as it remains in the schema.

**Evidence:**

- Schema marks `fullName` with `@deprecated(reason: "Use displayName")`.
- Persisted query usage shows active reads.
- Generated mobile client still has `fullName` in one fragment.
- No migration PR exists for that client.

**Required before merge:**

- Keep field in schema.
- Migrate generated clients and persisted queries.
- Track field-level usage until it reaches zero.
- Remove only after client release and observation window.

**Recommended cleanup path:**

- Continue deprecation and migrate consumers; removal is premature.

### Why this is a classic trap

A schema field can be entirely unused by server code and still be heavily used by clients.

---

## Example 17 — Compatibility adapter for renamed package export

### Situation

A shared TypeScript package exports both `createClient` and old alias `makeClient`. Internal repos use `createClient`. A PR removes `makeClient`.

### Nuance

Shared packages have consumers outside the local repo. The removability standard depends on whether the package is private, public, versioned, or consumed through lockfiles in downstream repos.

### Legacy Support Adjudication Verdict

**Verdict:** REMOVE  
**Confidence:** Medium  
**Risk:** P2  
**Legacy contract:** Shared package exposes `makeClient` as a renamed alias for `createClient`.  
**Consumer reality:** Monorepo search shows no internal use; private registry download logs show only current workspace consumers.  
**Producer reality:** New package versions expose canonical `createClient`; old consumers pinned to previous versions are unaffected by deleting alias in the next major/internal release.

**Evidence:**

- Monorepo search found no `makeClient` imports.
- Package is private and consumed only by controlled internal workspaces.
- Changelog announced the rename two releases ago.
- Tests cover canonical `createClient`.

**Required before merge:**

- Make removal part of a major/internal breaking-change release if semantic versioning is enforced.
- Add changelog entry and migration note.
- Verify downstream lockfile updates in the release PR.

**Recommended cleanup path:**

- Remove alias in the planned release branch.

### What would change the verdict?

For a public npm package, this would likely require a longer deprecation period and public usage/migration evidence.

---

## Example 18 — “Temporary” data repair job still protects against delayed external sync

### Situation

A cron job repairs records where `external_user_id` is missing after third-party sync. It was labeled `temporary` a year ago. A PR deletes it because the sync bug was fixed.

### Nuance

Repair jobs may remain necessary because old bad data, retries, delayed imports, or external outages continue to create the repaired condition.

### Legacy Support Adjudication Verdict

**Verdict:** DEPLOY OBSERVABILITY  
**Confidence:** Low  
**Risk:** P1  
**Legacy contract:** Repair job fills missing `external_user_id` for records affected by historical or delayed sync failures.  
**Consumer reality:** The job’s direct users are not people but data invariants and downstream systems expecting the field.  
**Producer reality:** Current sync bug is fixed, but delayed imports, retries, and third-party outage modes may still create missing values.

**Evidence:**

- Bugfix PR claims new writes include `external_user_id`.
- Cron job still modified 17 records in the last 30 days.
- No breakdown shows whether those records came from old backlog or new failures.

**Required before merge:**

- Do not delete yet.
- Add metrics distinguishing old backlog repair from newly-created missing IDs.
- Alert if new missing IDs are created.
- Run data scan after one full external sync cycle.

**Recommended cleanup path:**

- Keep job but narrow scope and add observability.
- Remove after it performs zero repairs over the agreed window and no new missing values appear.

### Why this is not dead code

A scheduled job can be rarely used and still essential when it repairs data corruption.

---

## Example 19 — Old deep links in mobile app

### Situation

The app supports old deep link format `myapp://profile?id=123`; new links use `myapp://users/123`. A PR removes the old route handler.

### Nuance

Deep links live outside the app: emails, SMS, push notifications, browser bookmarks, QR codes, old marketing pages, and user-shared links.

### Legacy Support Adjudication Verdict

**Verdict:** DEPRECATE  
**Confidence:** Medium  
**Risk:** P2  
**Legacy contract:** App opens historical profile deep links with query parameter `id`.  
**Consumer reality:** Current app generates new links, but old links may exist in notifications, emails, and user-shared messages.  
**Producer reality:** New producers emit canonical links; old external artifacts can still invoke old links.

**Evidence:**

- Current link generator uses `/users/:id`.
- Email templates were migrated three months ago.
- Push notification archive and public marketing links were not checked.
- Link open analytics still show low but nonzero old-format opens.

**Required before merge:**

- Keep handler but route it through a small legacy link adapter.
- Add analytics for old-format opens by source.
- Remove or redirect old links in public/static surfaces.

**Recommended cleanup path:**

- Deprecate the old handler and remove after link analytics reach zero or after the team accepts breakage of old external artifacts.

### Why this is subtle

The app may no longer create old links, but the internet remembers them.

---

## Example 20 — Test fixture appears legacy but encodes a real regression case

### Situation

A PR removes old JSON fixtures with `schemaVersion: 1` because production now writes `schemaVersion: 3`. The fixtures are used only in tests.

### Nuance

Test-only legacy data is not always junk. It may preserve regression coverage for imports, migrations, or restored historical records.

### Legacy Support Adjudication Verdict

**Verdict:** QUARANTINE  
**Confidence:** Medium  
**Risk:** P2  
**Legacy contract:** Test suite preserves ability to read/migrate historical `schemaVersion: 1` objects.  
**Consumer reality:** No production writer emits V1, but import/migration code still claims to support V1.  
**Producer reality:** Historical backups and customer exports can still contain V1.

**Evidence:**

- Current writer emits V3.
- V1 fixture is referenced by migration tests.
- Import docs still say V1–V3 are accepted.
- No data scan proves historical V1 imports are impossible.

**Required before merge:**

- Do not delete fixture without changing the support policy.
- Move fixture under `fixtures/legacy/schema-v1/` with explicit comments.
- Add a removal criterion tied to import policy.

**Recommended cleanup path:**

- Quarantine fixture and support code as legacy import compatibility.
- Remove only when V1 import support is formally ended.

### Why not REMOVE?

Deleting the fixture may silently delete the only proof that a promised migration path still works.

---

## Example 21 — Old environment variable name in deployment config

### Situation

The service reads both `DATABASE_URL` and older `POSTGRES_URL`. A PR removes `POSTGRES_URL` support because all Kubernetes manifests use `DATABASE_URL`.

### Nuance

Environment variables can come from many sources: local `.env`, CI secrets, preview deployments, serverless config, Helm charts, Terraform, one-off scripts, and developer docs.

### Legacy Support Adjudication Verdict

**Verdict:** REMOVE  
**Confidence:** Medium  
**Risk:** P2  
**Legacy contract:** Service accepts old env var `POSTGRES_URL` as fallback for `DATABASE_URL`.  
**Consumer reality:** Production and staging manifests use `DATABASE_URL`; preview and CI configs were checked and updated.  
**Producer reality:** Supported deployments should no longer provide only `POSTGRES_URL`.

**Evidence:**

- Kubernetes manifests use `DATABASE_URL`.
- Terraform, CI, and preview deployment templates use `DATABASE_URL`.
- Developer docs were updated.
- Repository search finds `POSTGRES_URL` only in the fallback code and old changelog.

**Required before merge:**

- Fail fast with a clear error if `DATABASE_URL` is missing.
- Mention removal in release notes.
- Remove stale docs and example `.env` entries.

**Recommended cleanup path:**

- Remove fallback now.

### Remaining risk

Individual developer machines may still have old `.env` files. That is acceptable if the error message is clear and docs are updated.

---

## Example 22 — Legacy payment processor path

### Situation

Checkout code still supports `processor="legacy_gateway"`; the company migrated to a new provider. A PR removes the old processor branch.

### Nuance

Payment paths require extreme caution. Refunds, chargebacks, reconciliation, subscriptions, dispute webhooks, and historical records may still depend on old processor identifiers after new purchases stop using them.

### Legacy Support Adjudication Verdict

**Verdict:** RETAIN  
**Confidence:** High  
**Risk:** P0  
**Legacy contract:** System can process lifecycle events for transactions originally created with `legacy_gateway`.  
**Consumer reality:** New checkouts use the new processor, but refunds, disputes, receipts, and reconciliation still reference historical legacy transactions.  
**Producer reality:** New purchases no longer produce `legacy_gateway`, but external payment webhooks and internal refund flows still can.

**Evidence:**

- Payment table contains historical rows with `legacy_gateway`.
- Refund service branches on original processor.
- Dispute webhook handler can still receive events for old transactions.
- Finance reconciliation export includes old processor IDs.

**Required before merge:**

- Do not remove lifecycle support.
- Separate “new purchase creation” from “historical transaction servicing.”
- Add tests for refund/dispute handling on legacy transactions.
- Ask payments/finance owner for explicit retirement criteria.

**Recommended cleanup path:**

- Block new purchases through the old processor if not already blocked.
- Retain historical lifecycle support until all refund/dispute/reconciliation obligations expire.

### Why this example matters

Some legacy paths must remain long after the old product path is closed because legal/financial lifecycle obligations continue.

---

# Common complex patterns and likely verdicts

| Pattern                                                 |                   Typical verdict | Why                                                      |
| ------------------------------------------------------- | --------------------------------: | -------------------------------------------------------- |
| Old field accepted by public API, no runtime data       |              DEPLOY OBSERVABILITY | Static evidence cannot prove no clients send it.         |
| Old field accepted by public API, active traffic exists |                         DEPRECATE | Consumers exist; migration path required.                |
| DB fallback after verified zero legacy rows             |                            REMOVE | Data reality can prove fallback is unnecessary.          |
| Old event schema with replay retention                  |                            RETAIN | Historical events are still valid inputs.                |
| Feature flag fallback used by incident playbook         |                        QUARANTINE | Not product-active, but operationally active.            |
| Mobile local cache migration                            | DEPRECATE or DEPLOY OBSERVABILITY | Dormant users and persisted state complicate removal.    |
| Old migration files                                     |                            RETAIN | Fresh database bootstrap may depend on them.             |
| Old package alias in private controlled monorepo        |                            REMOVE | Controlled consumers and release process lower risk.     |
| Old package alias in public SDK                         |                         DEPRECATE | External consumers require lifecycle policy.             |
| Auth/session compatibility                              |    DEPLOY OBSERVABILITY or RETAIN | Token lifetime and login safety raise evidence standard. |
| Payment/refund historical support                       |                            RETAIN | Lifecycle obligations outlive new transaction creation.  |

---

# Anti-patterns in weak review comments

Avoid comments like these:

> “No references found, delete it.”

Better:

> “No local references found. Before deletion, we need to know whether this is only an internal helper or whether external clients/data/jobs can still produce this shape.”

---

> “This was added years ago, so it is probably safe to remove.”

Better:

> “The age of the code tells us to investigate, not delete. Let’s recover why it was added and whether the support contract still exists.”

---

> “The current frontend does not use it.”

Better:

> “The current frontend does not use it, but the contract may also include mobile apps, SDKs, public API callers, cached payloads, old deep links, jobs, or persisted data.”

---

> “Tests pass without it.”

Better:

> “Tests passing is useful E1 evidence. For this risk class, we also need data/runtime/contract evidence because tests may not represent old clients or historical data.”

---

# Mini examples for quick code-review use

## Mini example A — Safe small removal

**Verdict:** REMOVE  
**Reason:** The legacy branch is an internal-only UI fallback for a prop that was removed from the component API. Search shows no callers, Storybook uses the new prop, and tests cover the canonical path. Risk is P3.

## Mini example B — Needs metric

**Verdict:** DEPLOY OBSERVABILITY  
**Reason:** This parser accepts an old webhook payload. We have no evidence that partners stopped sending it. Add a metric for old-payload matches before removal.

## Mini example C — Keep but isolate

**Verdict:** QUARANTINE  
**Reason:** The old branch is probably technical debt, but it still appears in rollback instructions. Move it behind `LegacyRollbackPath` and track execution.

## Mini example D — Formal sunset

**Verdict:** DEPRECATE  
**Reason:** The endpoint has active low-volume external traffic. Removing it now breaks known consumers; start a dated migration path.

## Mini example E — Must retain

**Verdict:** RETAIN  
**Reason:** The legacy parser handles historical events that can still be replayed from retention. Current producers are irrelevant until replay guarantees change.
