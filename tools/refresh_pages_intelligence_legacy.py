#!/usr/bin/env python3
"""Refresh page-visible GHE size, Git contribution metrics, and Work Ledger integration records.

The command is dry-run by default. Add --apply to write:
  docs/_data/repository.json
  docs/_data/contributions.json
  work-ledger/contributions.json
  work-ledger/contributions.csv
  work-ledger/activity-events.csv

Contribution figures are derived from non-merge Git commits affecting the document-owned
paths listed in document.json. "Words touched" equals token-level additions plus measured
removals. Under the default baseline adjustment, inherited template removals in the first
measured change to each tracked file are recorded separately and excluded from share; later
replacements count both removed and added tokens. The metric is activity evidence, not a
quality, approval, complexity, or performance score.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import difflib
import io
import json
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

DEFAULT_TRACKED_PATHS = (
    "docs/index.md",
    "docs/_data/document.json",
    "docs/_data/revisions.json",
    "docs/attachments",
)
GENERATED_PATHS = {
    "docs/_data/repository.json",
    "docs/_data/contributions.json",
    "work-ledger/contributions.json",
    "work-ledger/contributions.csv",
    "work-ledger/activity-events.csv",
}
BOT_MARKERS = ("[bot]", "github-actions", "dependabot", "renovate")
TOKEN_RE = re.compile(r"(?u)\b[\w][\w'’.-]*\b")
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
POLICY = "Under 1 GiB healthy; 1–5 GiB review; 5 GiB or larger corrective action"
METRIC_DEFINITION = (
    "Baseline-adjusted words touched equals token-level additions plus measured removals in document-owned paths "
    "after the configured baseline. With the default exclude-first-change-removals adjustment, inherited template "
    "words removed in the first measured change to each tracked file are recorded separately and excluded from share; "
    "subsequent replacements count both the removed token and the added token. Percent share is each human "
    "contributor's baseline-adjusted words touched divided by all human baseline-adjusted words touched in the "
    "measured Git history."
)
BASELINE_ADJUSTMENTS = {"exclude-first-change-removals", "none"}
METRIC_CAUTION = (
    "This is repository activity evidence only. It does not measure quality, correctness, "
    "difficulty, approval authority, operational impact, or work performed outside this repository, "
    "and it must not be used as the sole basis for personnel or performance decisions."
)


def run(command: list[str], *, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"required JSON file not found: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot read JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")
    return value


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text, encoding="utf-8", newline="\n")
    temp.replace(path)


def format_bytes(value: int) -> str:
    amount = float(max(0, value))
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(amount)} {unit}"
            precision = 2 if amount < 100 else 1
            return f"{amount:.{precision}f} {unit}"
        amount /= 1024
    raise AssertionError("unreachable")


def size_band(size_bytes: int) -> str:
    gib = size_bytes / (1024 ** 3)
    if gib < 1:
        return "healthy"
    if gib < 5:
        return "review"
    return "critical"


def valid_repository_name(value: str) -> bool:
    parts = value.strip().strip("/").split("/")
    if len(parts) != 2 or not all(parts):
        return False
    joined = " ".join(parts).casefold()
    return not ((parts[0].casefold() == "owner" and parts[1].casefold() == "repository") or any(word in joined for word in ("replace", "example")))


def query_repository_api(document: dict[str, Any]) -> tuple[str, str, int, str] | None:
    repository = os.environ.get("GITHUB_REPOSITORY", "").strip() or str(document.get("source_repository", "")).strip()
    api_url = os.environ.get("GITHUB_API_URL", "").strip().rstrip("/")
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    host = str(document.get("ghe_host", "")).strip()

    if valid_repository_name(repository) and api_url and token:
        request = urllib.request.Request(
            f"{api_url}/repos/{repository}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "controlled-manual-pages-metrics",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            size_kib = int(payload["size"])
            html_url = str(payload.get("html_url", ""))
            return repository, host or api_url, max(0, size_kib) * 1024, (
                f"GitHub Enterprise REST API Get a repository endpoint{f' ({html_url})' if html_url else ''}"
            )
        except (urllib.error.URLError, TimeoutError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            pass

    if valid_repository_name(repository) and host and shutil.which("gh"):
        result = run(["gh", "api", "--hostname", host, f"repos/{repository}"])
        if result.returncode == 0:
            try:
                payload = json.loads(result.stdout)
                size_kib = int(payload["size"])
                return repository, host, max(0, size_kib) * 1024, "GitHub Enterprise REST API via GitHub CLI"
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                pass
    return None


def git_available(root: Path) -> bool:
    if shutil.which("git") is None:
        return False
    result = run(["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"])
    return result.returncode == 0 and result.stdout.strip().casefold() == "true"


def git_value(root: Path, *args: str) -> str:
    result = run(["git", "-C", str(root), *args])
    return result.stdout.strip() if result.returncode == 0 else ""


def git_object_size(root: Path) -> int | None:
    result = run(["git", "-C", str(root), "count-objects", "-v"])
    if result.returncode != 0:
        return None
    values: dict[str, int] = {}
    for line in result.stdout.splitlines():
        key, sep, raw = line.partition(":")
        if not sep:
            continue
        try:
            values[key.strip()] = int(raw.strip())
        except ValueError:
            continue
    if "size" not in values and "size-pack" not in values:
        return None
    return (values.get("size", 0) + values.get("size-pack", 0)) * 1024


def working_tree_size(root: Path) -> int:
    excluded_parts = {
        ".git", ".template-backup", "_site", ".jekyll-cache", ".sass-cache",
        "__pycache__", ".pytest_cache", ".mypy_cache", ".venv", "venv", "node_modules",
    }
    total = 0
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel in GENERATED_PATHS or any(part in excluded_parts for part in path.relative_to(root).parts):
            continue
        try:
            total += path.stat().st_size
        except OSError:
            continue
    return total


def normalize_paths(document: dict[str, Any]) -> list[str]:
    raw = document.get("contribution_paths", DEFAULT_TRACKED_PATHS)
    if not isinstance(raw, list):
        raw = list(DEFAULT_TRACKED_PATHS)
    paths: list[str] = []
    for item in raw:
        value = str(item).strip().replace("\\", "/").strip("/")
        if not value or value.startswith(".") or value in GENERATED_PATHS:
            continue
        if value not in paths:
            paths.append(value)
    return paths or list(DEFAULT_TRACKED_PATHS)


def is_bot(name: str, email: str) -> bool:
    combined = f"{name} {email}".casefold()
    return any(marker in combined for marker in BOT_MARKERS)


def account_from_email(email: str) -> str:
    local, sep, domain = email.strip().partition("@")
    if not sep or "noreply" not in domain.casefold():
        return ""
    local = re.sub(r"^\d+\+", "", local)
    return local if local and local.casefold() not in {"noreply", "github-actions[bot]"} else ""


def identity_key(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def configured_value(mapping: Any, *keys: str) -> str:
    if not isinstance(mapping, dict):
        return ""
    normalized = {identity_key(str(key)): str(value).strip() for key, value in mapping.items()}
    for key in keys:
        if key and identity_key(key) in normalized:
            return normalized[identity_key(key)]
    return ""


def creator_identity(document: dict[str, Any]) -> tuple[str, str, str, str, set[str]]:
    creator = document.get("creator", {})
    if not isinstance(creator, dict):
        creator = {}
    name = str(creator.get("name", "")).strip()
    account = str(creator.get("account", "")).strip()
    work_ledger_id = str(creator.get("work_ledger_id", "")).strip()
    position_number = str(creator.get("position_number", "")).strip()
    aliases = {identity_key(name)} if name else set()
    raw_aliases = creator.get("aliases", [])
    if isinstance(raw_aliases, list):
        aliases.update(identity_key(str(value)) for value in raw_aliases if str(value).strip())
    if account:
        aliases.add(identity_key(account))
    return name, account, work_ledger_id, position_number, aliases


def git_text(root: Path, ref: str | None, path: str) -> str:
    if ref is None:
        return ""
    result = run(["git", "-C", str(root), "show", f"{ref}:{path}"], timeout=120)
    if result.returncode != 0 or "\x00" in result.stdout:
        return ""
    return result.stdout


def word_delta(old_text: str, new_text: str) -> tuple[int, int]:
    old_tokens = TOKEN_RE.findall(old_text)
    new_tokens = TOKEN_RE.findall(new_text)
    matcher = difflib.SequenceMatcher(a=old_tokens, b=new_tokens, autojunk=True)
    added = 0
    removed = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in {"replace", "delete"}:
            removed += i2 - i1
        if tag in {"replace", "insert"}:
            added += j2 - j1
    return added, removed


def nearest_heading(lines: list[str], line_number: int) -> str:
    if not lines:
        return ""
    index = min(max(line_number - 1, 0), len(lines) - 1)
    for position in range(index, -1, -1):
        match = re.match(r"^#{1,3}\s+(.+?)\s*$", lines[position])
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip()
    return ""


def section_labels(root: Path, parent: str | None, commit: str, path: str) -> list[str]:
    if path == "docs/_data/document.json":
        return ["Document identity and control metadata"]
    if path == "docs/_data/revisions.json":
        return ["Controlled revision record"]
    if not path.lower().endswith((".md", ".markdown")):
        return [Path(path).name]

    old_lines = git_text(root, parent, path).splitlines()
    new_lines = git_text(root, commit, path).splitlines()
    if parent:
        diff = run(["git", "-C", str(root), "diff", "--unified=0", parent, commit, "--", path], timeout=120)
    else:
        diff = run(["git", "-C", str(root), "show", "--format=", "--unified=0", commit, "--", path], timeout=120)
    labels: list[str] = []
    if diff.returncode == 0:
        for line in diff.stdout.splitlines():
            match = HUNK_RE.match(line)
            if not match:
                continue
            old_start = int(match.group(1))
            old_count = int(match.group(2) or "1")
            new_start = int(match.group(3))
            new_count = int(match.group(4) or "1")
            range_lines = new_lines if new_count else old_lines
            range_start = new_start if new_count else old_start
            range_count = new_count if new_count else old_count
            start_index = max(range_start - 1, 0)
            end_index = min(len(range_lines), start_index + max(range_count, 1))
            hunk_labels: list[str] = []
            for candidate in range_lines[start_index:end_index]:
                heading_match = re.match(r"^#{1,3}\s+(.+?)\s*$", candidate)
                if heading_match:
                    heading = re.sub(r"\s+", " ", heading_match.group(1)).strip()
                    if heading and heading not in hunk_labels:
                        hunk_labels.append(heading)
            if not hunk_labels:
                label = nearest_heading(range_lines, range_start)
                if label:
                    hunk_labels.append(label)
            for label in hunk_labels:
                if label not in labels:
                    labels.append(label)
    return labels or [Path(path).name]


def resolve_baseline(root: Path, tracked_paths: list[str], contribution_config: dict[str, Any]) -> tuple[str, str]:
    mode = str(contribution_config.get("baseline_mode", "after-initial-commit")).strip() or "after-initial-commit"
    explicit = str(contribution_config.get("baseline_commit", "")).strip()
    if explicit:
        verified = git_value(root, "rev-parse", "--verify", explicit + "^{commit}")
        if not verified:
            raise RuntimeError(f"configured baseline_commit does not resolve: {explicit}")
        return mode, verified
    if mode == "after-initial-commit":
        result = run(["git", "-C", str(root), "log", "--reverse", "--format=%H", "--", *tracked_paths], timeout=120)
        commits = [line.strip() for line in result.stdout.splitlines() if line.strip()] if result.returncode == 0 else []
        return mode, (commits[0] if commits else "")
    if mode == "all-history":
        return mode, ""
    raise RuntimeError("contribution-config baseline_mode must be 'after-initial-commit' or 'all-history'")


def commit_records(root: Path, tracked_paths: list[str], max_commits: int, baseline_commit: str) -> list[dict[str, str]]:
    pretty = "%H%x1f%h%x1f%ad%x1f%aN%x1f%aE%x1f%s%x1e"
    command = [
        "git", "-C", str(root), "log", "--no-merges", "--use-mailmap", "--date=short",
        f"--max-count={max_commits}", f"--pretty=format:{pretty}",
    ]
    if baseline_commit:
        command.append(f"{baseline_commit}..HEAD")
    command.extend(["--", *tracked_paths])
    result = run(command, timeout=120)
    if result.returncode != 0:
        return []
    records: list[dict[str, str]] = []
    for raw in result.stdout.split("\x1e"):
        raw = raw.strip("\r\n ")
        if not raw:
            continue
        fields = raw.split("\x1f", 5)
        if len(fields) != 6:
            continue
        commit, short, date, name, email, subject = (field.strip() for field in fields)
        records.append({
            "commit": commit,
            "short_commit": short,
            "date": date,
            "name": name or "Unknown Git author",
            "email": email,
            "subject": subject or "No commit subject supplied",
        })
    return records


def parent_commit(root: Path, commit: str) -> str | None:
    value = git_value(root, "rev-list", "--parents", "-n", "1", commit).split()
    return value[1] if len(value) > 1 else None


def changed_files(root: Path, commit: str, tracked_paths: list[str]) -> list[str]:
    result = run([
        "git", "-C", str(root), "diff-tree", "--root", "--no-commit-id", "--name-only", "-r",
        commit, "--", *tracked_paths,
    ], timeout=120)
    if result.returncode != 0:
        return []
    files: list[str] = []
    for line in result.stdout.splitlines():
        path = line.strip().replace("\\", "/")
        if path and path not in GENERATED_PATHS and path not in files:
            files.append(path)
    return files


def build_contributions(
    root: Path,
    document: dict[str, Any],
    tracked_paths: list[str],
    recent_limit: int,
    max_commits: int,
    generated_at: str,
    contribution_config: dict[str, Any],
) -> dict[str, Any]:
    creator_name, creator_account, creator_work_ledger, creator_position, creator_aliases = creator_identity(document)
    alias_map = contribution_config.get("aliases", {})
    account_map = contribution_config.get("accounts", {})
    work_ledger_map = contribution_config.get("work_ledger_ids", {})
    position_map = contribution_config.get("position_numbers", {})
    excluded_names = {
        identity_key(str(value))
        for value in contribution_config.get("excluded_authors", [])
        if str(value).strip()
    }
    baseline_mode, baseline_commit = resolve_baseline(root, tracked_paths, contribution_config)
    requested_adjustment = str(
        contribution_config.get("baseline_adjustment", "exclude-first-change-removals")
    ).strip() or "exclude-first-change-removals"
    if requested_adjustment not in BASELINE_ADJUSTMENTS:
        raise RuntimeError(
            "contribution-config baseline_adjustment must be 'exclude-first-change-removals' or 'none'"
        )
    effective_adjustment = requested_adjustment if baseline_commit else "none"
    source_commit = git_value(root, "log", "-1", "--format=%h", "--", *tracked_paths) or "Working tree"
    branch = git_value(root, "branch", "--show-current") or "Detached HEAD"

    records = commit_records(root, tracked_paths, max_commits, baseline_commit)
    changed_files_cache = {
        record["commit"]: changed_files(root, record["commit"], tracked_paths)
        for record in records
    }
    first_human_change_by_path: dict[str, str] = {}
    if effective_adjustment == "exclude-first-change-removals":
        for record in reversed(records):
            raw_account = account_from_email(record["email"])
            if is_bot(record["name"], record["email"]) or any(
                identity_key(value) in excluded_names
                for value in (record["name"], record["email"], raw_account)
                if value
            ):
                continue
            for changed_path in changed_files_cache.get(record["commit"], []):
                first_human_change_by_path.setdefault(changed_path, record["commit"])

    aggregate: dict[str, dict[str, Any]] = {}
    activity_events: list[dict[str, Any]] = []
    excluded_automation = 0
    skipped_binary_or_empty = 0
    total_excluded_template_removals = 0

    for record in records:
        raw_account = account_from_email(record["email"])
        if is_bot(record["name"], record["email"]) or any(
            identity_key(value) in excluded_names
            for value in (record["name"], record["email"], raw_account)
            if value
        ):
            excluded_automation += 1
            continue
        files = changed_files_cache.get(record["commit"], [])
        if not files:
            continue
        parent = parent_commit(root, record["commit"])
        added = 0
        removed = 0
        raw_removed = 0
        excluded_template_removed = 0
        sections: list[str] = []
        measured_files: list[str] = []
        for changed_path in files:
            old_text = git_text(root, parent, changed_path)
            new_text = git_text(root, record["commit"], changed_path)
            if not old_text and not new_text:
                skipped_binary_or_empty += 1
                continue
            file_added, file_raw_removed = word_delta(old_text, new_text)
            file_excluded_removed = (
                file_raw_removed
                if effective_adjustment == "exclude-first-change-removals"
                and first_human_change_by_path.get(changed_path) == record["commit"]
                else 0
            )
            file_removed = file_raw_removed - file_excluded_removed
            added += file_added
            raw_removed += file_raw_removed
            removed += file_removed
            excluded_template_removed += file_excluded_removed
            measured_files.append(changed_path)
            for label in section_labels(root, parent, record["commit"], changed_path):
                if label not in sections:
                    sections.append(label)

        words_touched = added + removed
        if not measured_files and words_touched == 0:
            continue
        total_excluded_template_removals += excluded_template_removed
        canonical_name = configured_value(alias_map, record["name"], record["email"], raw_account) or record["name"]
        account = configured_value(account_map, canonical_name, record["name"], record["email"], raw_account) or raw_account
        is_creator = (
            any(
                identity_key(value) in creator_aliases
                for value in (record["name"], canonical_name, account)
                if value
            )
            if creator_aliases
            else False
        )
        if is_creator and creator_account:
            account = creator_account
        display_name = creator_name if is_creator and creator_name else canonical_name
        work_ledger_id = (
            creator_work_ledger
            if is_creator and creator_work_ledger
            else configured_value(work_ledger_map, display_name, account, record["name"], record["email"])
        )
        position_number = (
            creator_position
            if is_creator and creator_position
            else configured_value(position_map, display_name, account, record["name"], record["email"])
        )
        work_ledger_id = work_ledger_id or "Unmapped"
        key = f"{identity_key(display_name)}|{identity_key(account)}|{identity_key(work_ledger_id)}"
        if key not in aggregate:
            aggregate[key] = {
                "name": display_name,
                "account": account,
                "is_creator": is_creator,
                "work_ledger_id": work_ledger_id,
                "position_number": position_number,
                "commits": 0,
                "words_added": 0,
                "raw_words_removed": 0,
                "excluded_template_words_removed": 0,
                "words_removed": 0,
                "words_touched": 0,
                "files": Counter(),
                "sections": Counter(),
                "first_contribution": record["date"],
                "latest_contribution": record["date"],
            }
        item = aggregate[key]
        item["commits"] += 1
        item["words_added"] += added
        item["raw_words_removed"] += raw_removed
        item["excluded_template_words_removed"] += excluded_template_removed
        item["words_removed"] += removed
        item["words_touched"] += words_touched
        item["first_contribution"] = min(item["first_contribution"], record["date"])
        item["latest_contribution"] = max(item["latest_contribution"], record["date"])
        item["files"].update(measured_files)
        item["sections"].update(sections)

        activity_events.append({
            "date": record["date"],
            "author": display_name,
            "account": account,
            "is_creator": is_creator,
            "work_ledger_id": work_ledger_id,
            "position_number": position_number,
            "commit": record["short_commit"],
            "subject": record["subject"],
            "words_added": added,
            "raw_words_removed": raw_removed,
            "excluded_template_words_removed": excluded_template_removed,
            "words_removed": removed,
            "words_touched": words_touched,
            "files": measured_files,
            "sections": sections[:6],
        })

    contributors_raw = sorted(
        aggregate.values(),
        key=lambda item: (-item["words_touched"], -item["commits"], item["name"].casefold()),
    )
    total_words = sum(item["words_touched"] for item in contributors_raw)
    contributors: list[dict[str, Any]] = []
    for rank, item in enumerate(contributors_raw, start=1):
        contributors.append({
            "rank": rank,
            "name": item["name"],
            "account": item["account"],
            "is_creator": bool(item["is_creator"]),
            "work_ledger_id": item["work_ledger_id"],
            "position_number": item["position_number"],
            "commits": item["commits"],
            "words_added": item["words_added"],
            "raw_words_removed": item["raw_words_removed"],
            "excluded_template_words_removed": item["excluded_template_words_removed"],
            "words_removed": item["words_removed"],
            "words_touched": item["words_touched"],
            "share_percent": round((item["words_touched"] / total_words) * 100, 1) if total_words else 0.0,
            "files_touched": [name for name, _ in item["files"].most_common(8)],
            "sections_touched": [name for name, _ in item["sections"].most_common(8)],
            "first_contribution": item["first_contribution"],
            "latest_contribution": item["latest_contribution"],
        })

    unmapped = sum(1 for item in contributors if item.get("work_ledger_id") == "Unmapped")
    status = (
        "generated-with-unmapped-ledgers" if unmapped else "generated"
    ) if contributors or activity_events else "no-measured-history"
    return {
        "schema_version": 1,
        "status": status,
        "generated_at": generated_at,
        "source": (
            "Non-merge Git author history for document-owned paths; identities normalized through .mailmap "
            "and contribution-config mappings when present"
        ),
        "source_commit": source_commit,
        "branch": branch,
        "baseline_mode": baseline_mode,
        "baseline_commit": (baseline_commit[:12] if baseline_commit else "Repository root"),
        "baseline_adjustment": effective_adjustment,
        "excluded_baseline_commits": (1 if baseline_commit else 0),
        "excluded_template_words_removed": total_excluded_template_removals,
        "tracked_paths": tracked_paths,
        "metric_name": "Baseline-adjusted words touched",
        "metric_definition": METRIC_DEFINITION,
        "metric_caution": METRIC_CAUTION,
        "total_contributors": len(contributors),
        "mapped_work_ledger_contributors": len(contributors) - unmapped,
        "unmapped_work_ledger_contributors": unmapped,
        "human_commits": sum(item["commits"] for item in contributors),
        "excluded_automation_commits": excluded_automation,
        "skipped_binary_or_empty_files": skipped_binary_or_empty,
        "total_words_added": sum(item["words_added"] for item in contributors),
        "total_raw_words_removed": sum(item["raw_words_removed"] for item in contributors),
        "total_words_removed": sum(item["words_removed"] for item in contributors),
        "total_words_touched": total_words,
        "contributors": contributors,
        "activity_event_count": len(activity_events),
        "activity_events": activity_events,
        "recent_edits": activity_events[:recent_limit],
        "work_ledger_records": {
            "json": "work-ledger/contributions.json",
            "csv": "work-ledger/contributions.csv",
            "activity_csv": "work-ledger/activity-events.csv",
        },
    }

def build_repository_data(root: Path, document: dict[str, Any], generated_at: str, require_ghe: bool) -> dict[str, Any]:
    api = query_repository_api(document)
    repository_name = os.environ.get("GITHUB_REPOSITORY", "").strip() or str(document.get("source_repository", "")).strip() or root.name
    host = str(document.get("ghe_host", "")).strip()
    if api:
        repository_name, source_host, size_bytes, source = api
        status = "ghe-api"
        host = source_host or host
    else:
        if require_ghe:
            raise RuntimeError(
                "GHE repository size could not be retrieved; verify GITHUB_API_URL/GITHUB_REPOSITORY/GITHUB_TOKEN "
                "or authenticated gh access plus document.ghe_host"
            )
        local = git_object_size(root) if git_available(root) else None
        if local is not None:
            size_bytes = local
            source = "Local Git object database fallback; not the authoritative GHE measurement"
            status = "local-git-fallback"
        else:
            size_bytes = working_tree_size(root)
            source = "Working-tree fallback; not the authoritative GHE measurement"
            status = "working-tree-fallback"
    return {
        "schema_version": 1,
        "repository": repository_name,
        "ghe_host": host,
        "size_kib": round(size_bytes / 1024),
        "size_bytes": size_bytes,
        "size_display": format_bytes(size_bytes),
        "size_band": size_band(size_bytes),
        "measured_at": generated_at,
        "source": source,
        "size_status": status,
        "policy": POLICY,
        "source_commit": git_value(root, "rev-parse", "--short=12", "HEAD") or "Working tree",
        "branch": git_value(root, "branch", "--show-current") or "Detached HEAD",
    }


def work_ledger_payload(document: dict[str, Any], contributions: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "document": {
            "document_id": document.get("document_id", ""),
            "title": document.get("title", ""),
            "document_type": document.get("document_type", ""),
            "version": document.get("version", ""),
            "repository": document.get("source_repository", ""),
            "creator": document.get("creator", {}),
        },
        "generated_at": contributions["generated_at"],
        "source_commit": contributions["source_commit"],
        "baseline_mode": contributions.get("baseline_mode", "all-history"),
        "baseline_commit": contributions.get("baseline_commit", "Repository root"),
        "baseline_adjustment": contributions.get("baseline_adjustment", "none"),
        "excluded_template_words_removed": contributions.get("excluded_template_words_removed", 0),
        "metric_name": contributions["metric_name"],
        "metric_definition": contributions["metric_definition"],
        "metric_caution": contributions["metric_caution"],
        "contributors": contributions["contributors"],
        "activity_events": contributions.get("activity_events", []),
        "activity_event_note": "Measured non-merge Git edits in the configured document scope; the repository Git history remains authoritative.",
    }


def work_ledger_csv(document: dict[str, Any], contributions: dict[str, Any]) -> str:
    buffer = io.StringIO(newline="")
    fields = [
        "document_id", "document_title", "document_type", "document_version", "repository",
        "baseline_mode", "baseline_commit", "baseline_adjustment",
        "rank", "contributor_name", "ghe_account", "work_ledger_id", "position_number", "is_creator", "commits",
        "words_added", "raw_words_removed", "excluded_template_words_removed", "words_removed", "words_touched", "share_percent",
        "files_touched", "sections_touched", "first_contribution", "latest_contribution",
        "source_commit", "generated_at", "metric_definition", "metric_caution",
    ]
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for contributor in contributions["contributors"]:
        writer.writerow({
            "document_id": document.get("document_id", ""),
            "document_title": document.get("title", ""),
            "document_type": document.get("document_type", ""),
            "document_version": document.get("version", ""),
            "repository": document.get("source_repository", ""),
            "baseline_mode": contributions.get("baseline_mode", "all-history"),
            "baseline_commit": contributions.get("baseline_commit", "Repository root"),
            "baseline_adjustment": contributions.get("baseline_adjustment", "none"),
            "rank": contributor["rank"],
            "contributor_name": contributor["name"],
            "ghe_account": contributor["account"],
            "work_ledger_id": contributor.get("work_ledger_id", "Unmapped"),
            "position_number": contributor.get("position_number", ""),
            "is_creator": str(contributor["is_creator"]).lower(),
            "commits": contributor["commits"],
            "words_added": contributor["words_added"],
            "raw_words_removed": contributor.get("raw_words_removed", contributor["words_removed"]),
            "excluded_template_words_removed": contributor.get("excluded_template_words_removed", 0),
            "words_removed": contributor["words_removed"],
            "words_touched": contributor["words_touched"],
            "share_percent": contributor["share_percent"],
            "files_touched": " | ".join(contributor["files_touched"]),
            "sections_touched": " | ".join(contributor["sections_touched"]),
            "first_contribution": contributor["first_contribution"],
            "latest_contribution": contributor["latest_contribution"],
            "source_commit": contributions["source_commit"],
            "generated_at": contributions["generated_at"],
            "metric_definition": contributions["metric_definition"],
            "metric_caution": contributions["metric_caution"],
        })
    return buffer.getvalue()


def work_ledger_activity_csv(document: dict[str, Any], contributions: dict[str, Any]) -> str:
    buffer = io.StringIO(newline="")
    fields = [
        "document_id", "document_title", "document_type", "document_version", "repository",
        "baseline_mode", "baseline_commit", "baseline_adjustment", "date", "commit", "contributor_name", "ghe_account",
        "work_ledger_id", "position_number", "is_creator", "commit_subject", "words_added",
        "raw_words_removed", "excluded_template_words_removed", "words_removed", "words_touched", "files", "sections", "source_commit", "generated_at",
        "metric_definition", "metric_caution",
    ]
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for event in contributions.get("activity_events", []):
        writer.writerow({
            "document_id": document.get("document_id", ""),
            "document_title": document.get("title", ""),
            "document_type": document.get("document_type", ""),
            "document_version": document.get("version", ""),
            "repository": document.get("source_repository", ""),
            "baseline_mode": contributions.get("baseline_mode", "all-history"),
            "baseline_commit": contributions.get("baseline_commit", "Repository root"),
            "baseline_adjustment": contributions.get("baseline_adjustment", "none"),
            "date": event.get("date", ""),
            "commit": event.get("commit", ""),
            "contributor_name": event.get("author", ""),
            "ghe_account": event.get("account", ""),
            "work_ledger_id": event.get("work_ledger_id", "Unmapped"),
            "position_number": event.get("position_number", ""),
            "is_creator": str(bool(event.get("is_creator"))).lower(),
            "commit_subject": event.get("subject", ""),
            "words_added": event.get("words_added", 0),
            "raw_words_removed": event.get("raw_words_removed", event.get("words_removed", 0)),
            "excluded_template_words_removed": event.get("excluded_template_words_removed", 0),
            "words_removed": event.get("words_removed", 0),
            "words_touched": event.get("words_touched", 0),
            "files": " | ".join(event.get("files", [])),
            "sections": " | ".join(event.get("sections", [])),
            "source_commit": contributions.get("source_commit", ""),
            "generated_at": contributions.get("generated_at", ""),
            "metric_definition": contributions.get("metric_definition", ""),
            "metric_caution": contributions.get("metric_caution", ""),
        })
    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Repository root")
    parser.add_argument("--recent-limit", type=int, default=30, help="Maximum page-visible recent edit entries")
    parser.add_argument("--max-commits", type=int, default=5000, help="Maximum non-merge commits measured")
    parser.add_argument("--require-ghe", action="store_true", help="Fail instead of using a clearly labeled local size fallback")
    parser.add_argument("--apply", action="store_true", help="Write generated JSON and CSV files")
    args = parser.parse_args()

    if not 1 <= args.recent_limit <= 250:
        raise SystemExit("ERROR: --recent-limit must be between 1 and 250")
    if not 1 <= args.max_commits <= 50000:
        raise SystemExit("ERROR: --max-commits must be between 1 and 50000")

    root = Path(args.repo).resolve()
    document_path = root / "docs/_data/document.json"
    try:
        document = load_json_object(document_path)
        config_path = root / "docs/_data/contribution-config.json"
        contribution_config = load_json_object(config_path) if config_path.is_file() else {}
        generated_at = utc_now()
        repository = build_repository_data(root, document, generated_at, args.require_ghe)
        tracked_paths = normalize_paths(document)
        if git_available(root):
            contributions = build_contributions(
                root, document, tracked_paths, args.recent_limit, args.max_commits, generated_at, contribution_config
            )
        else:
            contributions = {
                "schema_version": 1,
                "status": "git-unavailable",
                "generated_at": generated_at,
                "source": "Git history unavailable",
                "source_commit": "Working tree",
                "branch": "Working tree",
                "baseline_mode": str(contribution_config.get("baseline_mode", "after-initial-commit")),
                "baseline_commit": "Not generated",
                "baseline_adjustment": str(contribution_config.get("baseline_adjustment", "exclude-first-change-removals")),
                "excluded_baseline_commits": 0,
                "excluded_template_words_removed": 0,
                "tracked_paths": tracked_paths,
                "metric_name": "Words touched",
                "metric_definition": METRIC_DEFINITION,
                "metric_caution": METRIC_CAUTION,
                "total_contributors": 0,
                "mapped_work_ledger_contributors": 0,
                "unmapped_work_ledger_contributors": 0,
                "human_commits": 0,
                "excluded_automation_commits": 0,
                "skipped_binary_or_empty_files": 0,
                "total_words_added": 0,
                "total_raw_words_removed": 0,
                "total_words_removed": 0,
                "total_words_touched": 0,
                "contributors": [],
                "activity_event_count": 0,
                "activity_events": [],
                "recent_edits": [],
                "work_ledger_records": {
                    "json": "work-ledger/contributions.json",
                    "csv": "work-ledger/contributions.csv",
                    "activity_csv": "work-ledger/activity-events.csv",
                },
            }
        ledger = work_ledger_payload(document, contributions)
        ledger_csv = work_ledger_csv(document, contributions)
        activity_csv = work_ledger_activity_csv(document, contributions)
    except RuntimeError as exc:
        raise SystemExit(f"ERROR: {exc}") from exc

    print(f"Repository        : {repository['repository']}")
    print(f"GHE size          : {repository['size_display']} ({repository['size_status']})")
    print(f"Source commit     : {contributions['source_commit']}")
    print(
        f"Baseline          : {contributions.get('baseline_mode')} · {contributions.get('baseline_commit')} · "
        f"{contributions.get('baseline_adjustment', 'none')}"
    )
    print(f"Tracked paths     : {', '.join(tracked_paths)}")
    print(f"Contributors      : {contributions['total_contributors']}")
    print(f"Unmapped ledgers  : {contributions.get('unmapped_work_ledger_contributors', 0)}")
    print(f"Human commits     : {contributions['human_commits']}")
    print(f"Words added       : {contributions['total_words_added']:,}")
    print(f"Words removed     : {contributions['total_words_removed']:,}")
    print(f"Template removed  : {contributions.get('excluded_template_words_removed', 0):,} excluded")
    print(f"Words touched     : {contributions['total_words_touched']:,}")
    print(f"Activity events   : {contributions.get('activity_event_count', 0)}")
    print(f"Recent edit rows  : {len(contributions['recent_edits'])}")

    if not args.apply:
        print("DRY RUN: add --apply to write Pages data and Work Ledger integration records.")
        return 0

    atomic_write(root / "docs/_data/repository.json", json.dumps(repository, indent=2, ensure_ascii=False) + "\n")
    atomic_write(root / "docs/_data/contributions.json", json.dumps(contributions, indent=2, ensure_ascii=False) + "\n")
    atomic_write(root / "work-ledger/contributions.json", json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
    atomic_write(root / "work-ledger/contributions.csv", ledger_csv)
    atomic_write(root / "work-ledger/activity-events.csv", activity_csv)
    print("UPDATED: docs/_data/repository.json")
    print("UPDATED: docs/_data/contributions.json")
    print("UPDATED: work-ledger/contributions.json")
    print("UPDATED: work-ledger/contributions.csv")
    print("UPDATED: work-ledger/activity-events.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
