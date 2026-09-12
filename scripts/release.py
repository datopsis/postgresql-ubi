#!/usr/bin/env python3
"""Validate immutable release identity and emit deterministic release metadata."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path


TAG_PATTERN = re.compile(
    r"^v(?P<postgresql>[0-9]+\.[0-9]+)-ubi(?P<ubi>[1-9][0-9]*)-"
    r"r(?P<date>[0-9]{8})\.(?P<sequence>[1-9][0-9]*)$"
)
SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


class ReleaseError(ValueError):
    """A release candidate violates the release contract."""


def fail(message: str) -> None:
    raise ReleaseError(message)


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid JSON from {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path} must contain a JSON object")
    return value


def container_args(path: Path) -> dict[str, str]:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"cannot read {path}: {exc}")
    pairs = re.findall(r'^ARG ([A-Z0-9_]+)="([^"]+)"$', content, re.MULTILINE)
    return dict(pairs)


def git(*arguments: str, cwd: Path) -> str:
    result = subprocess.run(
        ["git", *arguments], cwd=cwd, check=False, capture_output=True, text=True
    )
    if result.returncode:
        fail(result.stderr.strip() or f"git {' '.join(arguments)} failed")
    return result.stdout.strip()


def strict_date(value: str) -> dt.date:
    try:
        parsed = dt.datetime.strptime(value, "%Y%m%d").date()
    except ValueError as exc:
        fail(f"release date {value!r} is not a real UTC calendar date: {exc}")
    if parsed.strftime("%Y%m%d") != value:
        fail(f"release date {value!r} is not canonical")
    return parsed


def validate_locks(root: Path, postgresql: str, ubi_major: str, args: dict[str, str]) -> None:
    inputs = load_json(root / "artifacts/lock-inputs.json")
    if inputs.get("postgresql_version") != postgresql:
        fail("tag PostgreSQL version does not match artifacts/lock-inputs.json")
    ubi_release = inputs.get("ubi_release")
    if not isinstance(ubi_release, str) or ubi_release.split(".", 1)[0] != ubi_major:
        fail("tag UBI major does not match artifacts/lock-inputs.json")

    expected_rpm = inputs.get("postgresql_rpm_version")
    if args.get("POSTGRESQL_VERSION") != postgresql:
        fail("tag PostgreSQL version does not match Containerfile")
    if args.get("POSTGRESQL_RPM_VERSION") != expected_rpm:
        fail("Containerfile PostgreSQL RPM version does not match lock inputs")

    expected_bases = inputs.get("base_images")
    container_bases = {
        "builder": args.get("UBI_MINIMAL_IMAGE"),
        "runtime": args.get("UBI_MICRO_IMAGE"),
    }
    if expected_bases != container_bases:
        fail("Containerfile base image references do not match lock inputs")

    for architecture in ("amd64", "arm64"):
        lock = load_json(root / f"artifacts/locks/{architecture}.json")
        if lock.get("architecture") != architecture:
            fail(f"{architecture} lock has the wrong architecture")
        if lock.get("postgresql_version") != postgresql:
            fail(f"{architecture} lock has the wrong PostgreSQL version")
        if lock.get("postgresql_rpm_version") != expected_rpm:
            fail(f"{architecture} lock has the wrong PostgreSQL RPM version")
        bases = lock.get("base_images")
        if not isinstance(bases, dict):
            fail(f"{architecture} lock has no base image map")
        for name, reference in expected_bases.items():
            item = bases.get(name)
            if not isinstance(item, dict) or item.get("reference") != reference:
                fail(f"{architecture} {name} base does not match lock inputs")
            digest = item.get("digest")
            if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
                fail(f"{architecture} {name} base digest is malformed")
            if not reference.endswith("@" + digest):
                fail(f"{architecture} {name} base reference/digest mismatch")


def validate_changelog(path: Path, tag: str, release_date: dt.date) -> None:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"cannot read {path}: {exc}")
    unreleased = content.find("## [Unreleased]")
    heading = f"## [{tag}] - {release_date.isoformat()}"
    release = content.find(heading)
    if unreleased < 0 or release < 0 or unreleased > release:
        fail(f"changelog must contain Unreleased followed by {heading!r}")
    if content.count(f"## [{tag}]") != 1:
        fail("changelog must contain the release heading exactly once")


def validate_git(
    root: Path,
    tag: str,
    release_date: str,
    sequence: int,
    require_annotated: bool,
    require_main: bool,
    require_next_sequence: bool,
) -> str:
    if require_annotated:
        git("cat-file", "-e", f"refs/tags/{tag}^{{tag}}", cwd=root)
    commit = git("rev-list", "-n", "1", tag, cwd=root)
    event_sha = os.environ.get("GITHUB_SHA")
    if event_sha and commit != event_sha:
        fail("release tag does not resolve to GITHUB_SHA")
    if require_main:
        git("rev-parse", "--verify", "refs/remotes/origin/main", cwd=root)
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, "refs/remotes/origin/main"],
            cwd=root,
            check=False,
        )
        if result.returncode:
            fail("release commit is not reachable from protected origin/main")
    if require_next_sequence:
        tags = git("tag", "--list", f"v*-r{release_date}.*", cwd=root).splitlines()
        sequences = []
        for known in tags:
            match = TAG_PATTERN.fullmatch(known)
            if known != tag and match:
                sequences.append(int(match.group("sequence")))
        expected = max(sequences, default=0) + 1
        if sequence != expected:
            fail(f"release sequence must be {expected}, not {sequence}")
    return commit


def validate_tag(namespace: argparse.Namespace) -> dict[str, str]:
    root = namespace.root.resolve()
    match = TAG_PATTERN.fullmatch(namespace.tag)
    if not match:
        fail(
            "release tag must match "
            "v<postgresql-version>-ubi<ubi-major>-r<YYYYMMDD>.<daily-sequence>"
        )
    release_date = strict_date(match.group("date"))
    if namespace.require_current_date:
        expected_date = os.environ.get("RELEASE_DATE_UTC")
        today = (
            strict_date(expected_date)
            if expected_date
            else dt.datetime.now(dt.timezone.utc).date()
        )
        if release_date != today:
            fail("release tag date is not the current UTC date")

    args = container_args(root / "Containerfile")
    validate_locks(root, match.group("postgresql"), match.group("ubi"), args)
    validate_changelog(root / "CHANGELOG.md", namespace.tag, release_date)
    commit = validate_git(
        root,
        namespace.tag,
        match.group("date"),
        int(match.group("sequence")),
        namespace.require_annotated,
        namespace.require_main,
        namespace.require_next_sequence,
    )
    values = {
        "tag": namespace.tag,
        "release_version": namespace.tag.removeprefix("v"),
        "postgresql_version": match.group("postgresql"),
        "ubi_major": match.group("ubi"),
        "release_date": release_date.isoformat(),
        "revision": commit,
        "commit_tag": f"sha-{commit[:12]}",
    }
    if namespace.github_output:
        with namespace.github_output.open("a", encoding="utf-8", newline="\n") as output:
            for key, value in values.items():
                output.write(f"{key}={value}\n")
    return values


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("tag")
    result.add_argument("--root", type=Path, default=Path("."))
    result.add_argument("--require-annotated", action="store_true")
    result.add_argument("--require-main", action="store_true")
    result.add_argument("--require-current-date", action="store_true")
    result.add_argument("--require-next-sequence", action="store_true")
    result.add_argument("--github-output", type=Path)
    return result


def main() -> int:
    try:
        values = validate_tag(parser().parse_args())
    except ReleaseError as exc:
        print(f"release validation failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(values, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
