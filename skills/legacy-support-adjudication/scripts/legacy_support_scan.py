#!/usr/bin/env python3
"""
Legacy Support Adjudication scanner.

This is a lightweight heuristic scanner for code-review agents. It does not prove
that legacy support is removable. It produces candidates that need adjudication.

Usage:
  python scripts/legacy_support_scan.py --root . --format markdown --output lsa-report.md
  python scripts/legacy_support_scan.py --root . --format json --output lsa-candidates.json
  python scripts/legacy_support_scan.py --root . --changed-only --base origin/main
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

DEFAULT_EXCLUDES = {
    ".git", "node_modules", ".next", "dist", "build", "coverage", ".venv", "venv",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "vendor", "target",
}

TEXT_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".go", ".rs", ".rb",
    ".php", ".cs", ".swift", ".m", ".mm", ".c", ".cc", ".cpp", ".h", ".hpp",
    ".sql", ".yml", ".yaml", ".json", ".toml", ".ini", ".env", ".md", ".txt",
    ".sh", ".bash", ".zsh", ".dockerfile", "",
}

PATTERNS = [
    ("legacy_keyword", re.compile(r"\b(legacy|compat|compatibility|backcompat|backward[-_ ]?compatibility)\b", re.I), "Possible compatibility boundary"),
    ("deprecation_keyword", re.compile(r"\b(deprecated|deprecation|sunset|end[-_ ]?of[-_ ]?life|EOL)\b", re.I), "Deprecation or sunset signal"),
    ("migration_keyword", re.compile(r"\b(migration|migrate|backfill|data repair|repair script|dual[-_ ]?(read|write))\b", re.I), "Migration or transitional data support"),
    ("old_format_keyword", re.compile(r"\b(old|previous|v1|v2|classic|transitional)[-_ ]?(schema|format|payload|client|api|field|route|model)?\b", re.I), "Old version/format support"),
    ("fallback_keyword", re.compile(r"\b(fallback|shim|adapter|polyfill|normalize|canonicalize|coerce|alias)\b", re.I), "Fallback/normalization logic"),
    ("todo_remove", re.compile(r"TODO[: ]+.*\b(remove|delete|cleanup|drop)\b|FIXME[: ]+.*\b(remove|delete|cleanup|drop)\b", re.I), "Comment says removal/cleanup is expected"),
    ("schema_fallback_js", re.compile(r"\w+(?:\.[A-Za-z_$][\w$]*|\[['\"][^'\"]+['\"]\])\s*(?:\?\?|\|\|)\s*\w+(?:\.[A-Za-z_$][\w$]*|\[['\"][^'\"]+['\"]\])"), "Possible field fallback expression"),
    ("schema_fallback_py", re.compile(r"\.get\(['\"][^'\"]+['\"]\)\s+or\s+\w+\.get\(['\"][^'\"]+['\"]\)"), "Possible Python dict field fallback"),
    ("api_lifecycle_header", re.compile(r"\b(Deprecation|Sunset)\b\s*[:=,)]"), "HTTP API lifecycle header"),
]

RISK_HINTS = [
    ("P0", re.compile(r"\b(auth|payment|billing|privacy|delete|deletion|security|compliance|encrypt|account)\b", re.I)),
    ("P1", re.compile(r"\b(public api|mobile|database|migration|queue|cron|worker|job|customer|integration|sdk|shared package)\b", re.I)),
    ("P2", re.compile(r"\b(admin|analytics|import|export|feature flag|experiment|internal api)\b", re.I)),
]

@dataclass
class Finding:
    file: str
    line: int
    pattern_id: str
    category: str
    snippet: str
    risk_hint: str = "P3"
    evidence_level: str = "E0"
    suggested_questions: list[str] = field(default_factory=list)


def run(cmd: list[str], cwd: Path) -> str:
    try:
        return subprocess.check_output(cmd, cwd=str(cwd), text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return ""


def changed_files(root: Path, base: str) -> set[Path]:
    out = run(["git", "diff", "--name-only", f"{base}...HEAD"], root)
    return {root / line.strip() for line in out.splitlines() if line.strip()}


def should_skip(path: Path, root: Path) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        rel_parts = path.parts
    if any(part in DEFAULT_EXCLUDES for part in rel_parts):
        return True
    if path.is_dir():
        return True
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return True
    if path.name.endswith((".lock", ".min.js", ".map")):
        return True
    return False


def iter_files(root: Path, only: set[Path] | None = None) -> Iterable[Path]:
    if only is not None:
        for path in sorted(only):
            if path.exists() and not should_skip(path, root):
                yield path
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in DEFAULT_EXCLUDES]
        for filename in filenames:
            path = Path(dirpath) / filename
            if not should_skip(path, root):
                yield path


def risk_for(text: str, file: str) -> str:
    haystack = f"{file}\n{text}"
    for risk, rx in RISK_HINTS:
        if rx.search(haystack):
            return risk
    return "P3"


def questions_for(pattern_id: str, risk: str) -> list[str]:
    base = [
        "What exact old contract is this path supporting?",
        "Who can still consume or produce this old shape?",
        "What evidence proves current systems cannot reach this path?",
    ]
    if risk in {"P0", "P1"}:
        base.append("What runtime/data/owner evidence is required before removal?")
    if "migration" in pattern_id or "schema" in pattern_id:
        base.append("Do persisted records, backups, queued jobs, or replays still require this reader?")
    if "deprecation" in pattern_id or "api" in pattern_id:
        base.append("Has a deprecation and sunset/migration path been communicated to consumers?")
    return base


def scan_file(root: Path, path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        text = path.read_text(errors="ignore")
    except Exception:
        return findings

    rel = str(path.relative_to(root))
    lines = text.splitlines()
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        for pattern_id, rx, category in PATTERNS:
            if rx.search(stripped):
                risk = risk_for(stripped, rel)
                findings.append(
                    Finding(
                        file=rel,
                        line=i,
                        pattern_id=pattern_id,
                        category=category,
                        snippet=stripped[:240],
                        risk_hint=risk,
                        suggested_questions=questions_for(pattern_id, risk),
                    )
                )
                break
    return findings


def summarize(findings: list[Finding]) -> dict:
    by_risk: dict[str, int] = {}
    by_pattern: dict[str, int] = {}
    for f in findings:
        by_risk[f.risk_hint] = by_risk.get(f.risk_hint, 0) + 1
        by_pattern[f.pattern_id] = by_pattern.get(f.pattern_id, 0) + 1
    return {"total": len(findings), "by_risk": by_risk, "by_pattern": by_pattern}


def render_markdown(findings: list[Finding], root: Path) -> str:
    summary = summarize(findings)
    out: list[str] = []
    out.append("# Legacy Support Adjudication Scan")
    out.append("")
    out.append(f"Root: `{root}`")
    out.append("")
    out.append("## Summary")
    out.append("")
    out.append(f"- Total candidates: **{summary['total']}**")
    out.append(f"- By risk hint: `{json.dumps(summary['by_risk'], sort_keys=True)}`")
    out.append(f"- By pattern: `{json.dumps(summary['by_pattern'], sort_keys=True)}`")
    out.append("")
    out.append("## Candidates")
    out.append("")
    if not findings:
        out.append("No candidates found by heuristic scan. This does not prove no legacy support exists.")
        return "\n".join(out)

    for idx, f in enumerate(findings, start=1):
        out.append(f"### LSA-{idx:03d} — `{f.file}:{f.line}`")
        out.append("")
        out.append(f"- **Pattern:** `{f.pattern_id}`")
        out.append(f"- **Category:** {f.category}")
        out.append(f"- **Risk hint:** {f.risk_hint}")
        out.append(f"- **Evidence level:** {f.evidence_level} suspicion only")
        out.append(f"- **Snippet:** `{f.snippet}`")
        out.append("- **Questions:**")
        for q in f.suggested_questions:
            out.append(f"  - {q}")
        out.append("- **Default recommendation:** investigate; do not remove based on this scan alone.")
        out.append("")
    return "\n".join(out)


def write_or_print(content: str, output: str | None) -> None:
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content + "\n", encoding="utf-8")
    else:
        print(content)


def main() -> None:
    parser = argparse.ArgumentParser(description="Find possible legacy-support logic for adjudication.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--output", help="Optional output file. Defaults to stdout.")
    parser.add_argument("--changed-only", action="store_true", help="Scan only files changed vs --base")
    parser.add_argument("--base", default="origin/main", help="Base ref for --changed-only")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    only = changed_files(root, args.base) if args.changed_only else None
    findings: list[Finding] = []
    for path in iter_files(root, only=only):
        findings.extend(scan_file(root, path))

    if args.format == "json":
        content = json.dumps({"summary": summarize(findings), "findings": [asdict(f) for f in findings]}, indent=2)
    else:
        content = render_markdown(findings, root)
    write_or_print(content, args.output)


if __name__ == "__main__":
    main()
