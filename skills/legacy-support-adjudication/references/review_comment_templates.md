# Review Comment Templates

## 1. Under-evidenced removal

I would not remove this yet. This looks like compatibility logic rather than simple dead code. Before deletion, please identify the legacy contract it supports, check whether any current clients/data/jobs can still produce that shape, and add evidence from runtime logs or data scans if this crosses a repo/API/database boundary.

## 2. Runtime evidence needed

Static search is a good start, but it does not prove this compatibility path is unused. Because this crosses a runtime boundary, please add usage evidence: endpoint hits, branch execution logs, feature flag exposure, client-version data, or a data scan over a representative window.

## 3. Data evidence needed

This fallback appears to support historical data shape(s). Please include a production-safe data scan or migration/backfill proof showing that no persisted records still require this reader before removing it.

## 4. Public/mobile API caution

This may still be part of a support contract for older clients. Please verify active client versions and the public API/deprecation policy before removing it. If consumers may still exist, this should be deprecated first rather than deleted immediately.

## 5. Quarantine suggestion

I agree this is technical debt, but the support contract is not proven dead. I recommend moving it behind a named compatibility boundary with tests and instrumentation. That gives us a safe path to remove it later without spreading the shim further.

## 6. Removal looks safe

This looks removable based on the evidence: no static consumers, current producers no longer emit the old shape, and runtime/data checks show no usage over the relevant window. Please keep the removal small, adjust tests around the canonical path, and include a rollback note if this is production-facing.

## 7. Keep but document

This compatibility path still appears required. Please add a short comment naming the legacy contract, the owner, and the condition under which it can be removed. That will prevent future reviewers from rediscovering the same context.

## 8. Deprecation path needed

This should probably become a deprecation rather than an immediate removal. The PR should define replacement behavior, identify known consumers, add deprecation signaling where appropriate, and create a dated removal criterion.
