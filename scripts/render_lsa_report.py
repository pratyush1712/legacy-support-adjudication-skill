#!/usr/bin/env python3
"""Render scanner JSON into a compact review report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_json", help="JSON output from legacy_support_scan.py")
    parser.add_argument("--top", type=int, default=25)
    args = parser.parse_args()

    data = json.loads(Path(args.input_json).read_text())
    findings = data.get("findings", [])[: args.top]

    print("# Legacy Support Adjudication Review Report")
    print()
    print("## Summary")
    print()
    print(f"- Total candidates: {data.get('summary', {}).get('total', 0)}")
    print(f"- Risk hints: `{json.dumps(data.get('summary', {}).get('by_risk', {}), sort_keys=True)}`")
    print()
    print("## Review-ready candidates")
    print()
    for i, f in enumerate(findings, start=1):
        print(f"### LSA-{i:03d}: `{f['file']}:{f['line']}`")
        print()
        print(f"**Risk hint:** {f['risk_hint']}  ")
        print(f"**Pattern:** `{f['pattern_id']}`  ")
        print(f"**Snippet:** `{f['snippet']}`")
        print()
        print("**Adjudication needed:**")
        for q in f.get("suggested_questions", []):
            print(f"- {q}")
        print()
        print("**Default verdict:** DEPLOY OBSERVABILITY or QUARANTINE unless stronger evidence is already available.")
        print()


if __name__ == "__main__":
    main()
