#!/usr/bin/env python3
"""Add or replace a controlled revision displayed on Pages.

The command is dry-run by default. Add --apply to write the revision register.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    if not path.is_file():
        raise SystemExit(f"ERROR: missing {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: cannot read {path}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Repository root")
    parser.add_argument("--version", required=True)
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument("--status", default="Reviewed")
    parser.add_argument("--editor", required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--approver", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--reference-url", default="")
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--set-current-version", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    try:
        dt.date.fromisoformat(args.date)
    except ValueError as exc:
        raise SystemExit(f"ERROR: --date must use YYYY-MM-DD: {exc}") from exc

    root = Path(args.repo).resolve()
    revision_path = root / "docs/_data/revisions.json"
    document_path = root / "docs/_data/document.json"
    revision_data = load_json(revision_path)
    document = load_json(document_path)

    if isinstance(revision_data, list):
        revision_data = {"schema_version": 1, "entries": revision_data}
    if not isinstance(revision_data, dict) or not isinstance(revision_data.get("entries"), list):
        raise SystemExit("ERROR: revisions.json must contain an object with an entries array")
    if not isinstance(document, dict):
        raise SystemExit("ERROR: document.json must contain an object")

    entry = {
        "version": args.version,
        "date": args.date,
        "status": args.status,
        "editor": args.editor,
        "reviewer": args.reviewer,
        "approver": args.approver,
        "summary": args.summary,
        "reference": args.reference,
        "reference_url": args.reference_url,
    }
    entries = revision_data["entries"]
    matches = [index for index, item in enumerate(entries) if isinstance(item, dict) and item.get("version") == args.version]
    if matches and not args.replace:
        raise SystemExit(f"ERROR: revision {args.version} already exists; use --replace")

    action = "REPLACE" if matches else "ADD"
    if matches:
        entries[matches[0]] = entry
    else:
        entries.insert(0, entry)

    print(f"{action}: {args.version} · {args.date} · editor={args.editor}")
    if args.set_current_version:
        print(f"DOCUMENT VERSION: {document.get('version')!r} -> {args.version!r}")
        document["version"] = args.version
    elif document.get("version") != args.version:
        print(f"WARNING: document current version is {document.get('version')!r}")

    if not args.apply:
        print("DRY RUN: add --apply to write the revision.")
        return 0

    revision_path.write_text(json.dumps(revision_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    if args.set_current_version:
        document_path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"UPDATED: {revision_path}")
    print("NEXT: python tools/refresh_pages_intelligence.py --repo . --apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
