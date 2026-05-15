# Legacy Support Adjudication Report

## Candidate

- **Candidate ID:** LSA-___
- **Location:** `path/to/file.ext:line`
- **Legacy contract:** 
- **Current PR/change:** 
- **Risk:** P0 | P1 | P2 | P3
- **Initial concern:** 

## Investigation

### 1. History

- Introduced by:
- Original reason:
- Linked issue/PR/migration/incident:
- Stated removal criterion, if any:

### 2. Static consumers

- Same package:
- Same repo:
- Adjacent repos/packages:
- Specs/generated clients/config:

### 3. Data/runtime consumers

- Data scan:
- Logs/traces/metrics:
- Feature flag exposure:
- Mobile/client version data:
- Jobs/queues/events:

### 4. Producer reality

Can current systems still create, receive, import, replay, cache, or hydrate the legacy shape?

- Yes/No/Unknown:
- Evidence:

### 5. Breakage analysis

- User-visible breakage:
- Operational breakage:
- Data-loss risk:
- Rollback risk:
- Test gaps:

## Verdict

**Verdict:** REMOVE | RETAIN | DEPRECATE | QUARANTINE | DEPLOY OBSERVABILITY  
**Confidence:** High | Medium | Low  
**Risk:** P0 | P1 | P2 | P3  

**Evidence:**
- 
- 
- 

**Required before merge:**
- 
- 

**Recommended cleanup path:**
- 
