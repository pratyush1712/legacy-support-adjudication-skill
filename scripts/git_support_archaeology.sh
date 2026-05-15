#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  git_support_archaeology.sh <token-or-file> [path]

Examples:
  git_support_archaeology.sh user_id
  git_support_archaeology.sh legacyPayload src/api/user.ts

What it does:
  - Shows current references for a token or file.
  - Shows commits that added/removed the token using git log -S.
  - Shows blame for a file when a path is provided.
USAGE
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

TOKEN="$1"
PATH_ARG="${2:-}"

echo "# Legacy Support Archaeology"
echo
echo "## Token/file"
echo "${TOKEN}"
echo

echo "## Current references"
if [[ -n "$PATH_ARG" ]]; then
  git grep -n --break --heading -I -- "$TOKEN" "$PATH_ARG" || true
else
  git grep -n --break --heading -I -- "$TOKEN" || true
fi

echo
echo "## History: git log -S"
if [[ -n "$PATH_ARG" ]]; then
  git log --all --date=short --pretty=format:'%h %ad %an %s' -S "$TOKEN" -- "$PATH_ARG" || true
else
  git log --all --date=short --pretty=format:'%h %ad %an %s' -S "$TOKEN" || true
fi

echo
echo
echo "## Blame"
if [[ -n "$PATH_ARG" && -f "$PATH_ARG" ]]; then
  git blame -L 1,220 --date=short -- "$PATH_ARG" || true
else
  echo "No file path supplied; skipping blame."
fi
