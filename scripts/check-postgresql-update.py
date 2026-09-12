#!/usr/bin/env python3
"""Create a fail-closed PostgreSQL upstream update report."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import urllib.request
from pathlib import Path


VERSIONS_URL = "https://www.postgresql.org/versions.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, default=Path("artifacts/lock-inputs.json"))
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--github-output", type=Path)
    arguments = parser.parse_args()

    inputs = json.loads(arguments.inputs.read_text(encoding="utf-8"))
    current = inputs["postgresql_version"]
    major = current.split(".", 1)[0]
    request = urllib.request.Request(
        VERSIONS_URL, headers={"User-Agent": "datopsis/postgresql-ubi update monitor"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        versions = json.load(response)
    selected = next(item for item in versions if item["major"] == major)
    latest = f"{major}.{selected['latestMinor']}"
    update_available = latest != current
    status = "UPDATE REVIEW REQUIRED" if update_available else "current"
    timestamp = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    report = f"""# PostgreSQL and supply-chain update monitor

Generated: `{timestamp}`

| Input | Locked/selected | Authoritative result | Status |
| --- | --- | --- | --- |
| PostgreSQL major {major} | `{current}` | `{latest}` (released {selected['relDate']}, EOL {selected['eolDate']}) | **{status}** |

Authoritative PostgreSQL data: {VERSIONS_URL}

The scheduled artifact-lock workflow separately resolves both native
architectures from current PGDG and UBI metadata and verifies every downloaded
RPM, source RPM, signing-key hash/fingerprint, and base digest. Review its
artifacts and failures; automation must never accept a changed key or lock.

Dependabot and Renovate propose pinned GitHub Action, Python tool, UBI image,
Syft, Grype, Trivy, Cosign, and assurance-tool updates. Scanner databases are
refreshed by scheduled CI and release runs. Every proposal still requires the
review and qualification in `docs/MAINTENANCE.md`.
"""
    arguments.report.write_text(report, encoding="utf-8", newline="\n")
    if arguments.github_output:
        with arguments.github_output.open("a", encoding="utf-8", newline="\n") as output:
            output.write(f"update_available={str(update_available).lower()}\n")
            output.write(f"current={current}\nlatest={latest}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
