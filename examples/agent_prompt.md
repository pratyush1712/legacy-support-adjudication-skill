# Agent Prompt: Legacy Support Adjudication in Code Review

Use this prompt when asking an agent to review a PR that touches possible legacy support.

```text
You are reviewing this PR with the Legacy Support Adjudication skill.

Goal: determine whether the compatibility logic touched by this PR is still required or safely removable.

Do not treat this as ordinary dead-code detection. For every legacy path, identify:
1. the old contract being supported,
2. actual and possible consumers,
3. whether current systems can still produce or receive the old shape,
4. what breaks if it disappears,
5. what evidence is strong enough for the risk level.

Use verdicts only from: RETAIN, DEPLOY OBSERVABILITY, DEPRECATE, QUARANTINE, REMOVE.

For each verdict, include confidence, risk, evidence, required-before-merge items, and recommended cleanup path.

Be explicit about unchecked layers. Do not invent runtime evidence.
```
