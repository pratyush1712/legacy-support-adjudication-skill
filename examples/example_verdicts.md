# Example Verdicts

## Example 1 — old API field alias

### Legacy Support Adjudication Verdict

**Verdict:** DEPLOY OBSERVABILITY  
**Confidence:** Low  
**Risk:** P1  
**Legacy contract:** Backend accepts `user_id` in addition to canonical `userId`.  
**Consumer reality:** Static repo search shows no current web client sends `user_id`, but mobile clients and third-party integrations were not checked.  
**Producer reality:** Current web producer emits only `userId`; old mobile versions may still emit `user_id`.  
**Evidence:**
- No local web references to `user_id`.
- No access-log or client-version evidence included.

**Required before merge:**
- Add temporary metric/log for requests using `user_id`.
- Check active mobile versions and third-party API docs.

**Recommended cleanup path:**
- Quarantine alias handling in `legacyPayloadAliases.ts`, observe for 30 days, then remove if zero usage and owners sign off.

## Example 2 — old database column reader

### Legacy Support Adjudication Verdict

**Verdict:** REMOVE  
**Confidence:** High  
**Risk:** P1  
**Legacy contract:** Reader falls back from `profile.display_name` to old nullable `profile.name`.  
**Consumer reality:** All current readers use `display_name`; old field is not exposed in API response.  
**Producer reality:** Writers stopped writing `name` in migration 2024-03-18; production scan shows zero rows where `display_name IS NULL AND name IS NOT NULL`.  
**Evidence:**
- Migration backfilled `display_name` and marked writer canonical.
- Production-safe scan shows zero legacy-only rows.
- API tests cover canonical field.

**Required before merge:**
- Add migration/assertion preventing new legacy-only rows.
- Keep rollback note for one deploy.

**Recommended cleanup path:**
- Remove fallback reader now; drop old column in a separate migration after one release.

## Example 3 — feature flag off-branch

### Legacy Support Adjudication Verdict

**Verdict:** QUARANTINE  
**Confidence:** Medium  
**Risk:** P2  
**Legacy contract:** Old recommendation algorithm remains behind `new_recs_enabled=false`.  
**Consumer reality:** Flag dashboard shows 100% enabled for production, but staging and emergency rollback still reference off-branch.  
**Producer reality:** Current requests can still execute old path if flag is flipped.  
**Evidence:**
- Flag config indicates old branch is not used in normal production traffic.
- Rollback policy still names this flag as the emergency fallback.

**Required before merge:**
- Move old algorithm to `legacy/recsFallback.ts`.
- Add alert if old branch executes in production.
- Create owner ticket to replace rollback strategy.

**Recommended cleanup path:**
- Do not delete until rollback playbook is updated and old branch has zero execution for the agreed observation window.
