#!/usr/bin/env python3
"""Render scanner JSON into a compact review report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_report(data: dict, top: int) -> str:
    findings = data.get("findings", [])[:top]
    lines: list[str] = []
    lines.append("# Legacy Support Adjudication Review Report")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total candidates: {data.get('summary', {}).get('total', 0)}")
    lines.append(f"- Risk hints: `{json.dumps(data.get('summary', {}).get('by_risk', {}), sort_keys=True)}`")
    lines.append("")
    lines.append("## Review-ready candidates")
    lines.append("")
    if not findings:
        lines.append("No candidates found by heuristic scan. This does not prove no legacy support exists.")
        return "\n".join(lines)

    for i, f in enumerate(findings, start=1):
        lines.append(f"### LSA-{i:03d}: `{f['file']}:{f['line']}`")
        lines.append("")
        lines.append(f"**Risk hint:** {f['risk_hint']}  ")
        lines.append(f"**Pattern:** `{f['pattern_id']}`  ")
        lines.append(f"**Snippet:** `{f['snippet']}`")
        lines.append("")
        lines.append("**Adjudication needed:**")
        for q in f.get("suggested_questions", []):
            lines.append(f"- {q}")
        lines.append("")
        lines.append("**Default verdict:** DEPLOY OBSERVABILITY or QUARANTINE unless stronger evidence is already available.")
        lines.append("")
    return "\n".join(lines)


def write_or_print(content: str, output: str | None) -> None:
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content + "\n", encoding="utf-8")
    else:
        print(content)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_json", help="JSON output from legacy_support_scan.py")
    parser.add_argument("--top", type=int, default=25)
    parser.add_argument("--output", help="Optional output file. Defaults to stdout.")
    args = parser.parse_args()

    data = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    write_or_print(build_report(data, args.top), args.output)


if __name__ == "__main__":
    main()
