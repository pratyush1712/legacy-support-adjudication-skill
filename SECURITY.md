# Security Policy

This repository contains an agent skill, examples, scanner scripts, and Semgrep starter rules. It does not run as a hosted service and does not collect data.

## Reporting a vulnerability

If you find a security issue in the scripts, examples, or recommended workflows, please open a private report if GitHub security advisories are enabled for the repository. Otherwise, contact the maintainer directly.

Please include:

- affected file or workflow
- reproduction steps
- expected impact
- suggested mitigation, if known

## Scope

Security-sensitive areas include:

- scripts that traverse repositories or read files
- shell commands in docs/examples
- Semgrep rules that could encourage unsafe review behavior
- recommendations involving auth, payments, privacy, deletion, compliance, or data retention

## Review posture

The skill intentionally treats auth, billing, privacy, deletion, security, and irreversible data mutation as high-risk domains. It should not recommend removal of compatibility paths in those areas without strong runtime, owner, and staged-rollout evidence.
