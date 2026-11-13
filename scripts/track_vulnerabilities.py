#!/usr/bin/env python3
"""Maintain one scheduled UBI availability issue; notify only on state changes."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from vulnerability_gate import summary

TITLE = "UBI vulnerability fix availability"
MARKER = "ubi-vulnerability-state"


def gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True,
                          text=True, timeout=60).stdout


def issue_body(directory, run_url):
    reports = []
    for arch in ("amd64", "arm64"):
        paths = list(directory.glob(f"**/vulnerability-gate-{arch}/gate.json"))
        if len(paths) != 1:
            report = dict(architecture=arch, findings=[], errors=["missing or ambiguous native gate report"])
        else:
            report = json.loads(paths[0].read_text())
            if report["architecture"] != arch:
                raise ValueError("gate report architecture mismatch")
        reports.append(report)
    # Exclude timestamps, run URLs and repository metadata churn. A new finding,
    # vendor version, installed version, decision or query error is a state change.
    state = [dict(architecture=r["architecture"], errors=sorted(r["errors"]), findings=sorted(
        [{key: row[key] for key in ("scanner", "id", "package", "installed", "severity",
                                   "fixed", "decision", "reason")} for row in r["findings"]],
        key=lambda row: json.dumps(row, sort_keys=True))) for r in reports]
    digest = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()
    body = (f"<!-- {MARKER}:{digest} -->\n"
            "This dashboard tracks High/Critical vendor fixes against the native UBI repositories.\n"
            "Deferred means the fixed RPM is not yet published there; it does not mean safe or resolved.\n"
            "Available fixes and uncertainty block the gate. Findings without a vendor fix remain reported.\n\n"
            f"Latest scheduled evidence: {run_url}\n\n" + "\n".join(summary(r) for r in reports))
    return digest, body


def publish(directory, run_url):
    digest, body = issue_body(directory, run_url)
    issues = json.loads(gh("issue", "list", "--state", "all", "--limit", "100",
                           "--search", f'"{TITLE}" in:title', "--json", "number,title,body,state"))
    matches = [i for i in issues if i["title"] == TITLE]
    if len(matches) > 1:
        raise ValueError("multiple tracking issues; refusing to update an ambiguous target")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "body.md"
        path.write_text(body)
        if not matches:
            gh("issue", "create", "--title", TITLE, "--body-file", str(path))
            return "created"
        issue = matches[0]
        if f"<!-- {MARKER}:" not in issue["body"]:
            raise ValueError("existing issue is not the managed tracking issue")
        old = re.search(rf"<!-- {MARKER}:([0-9a-f]{{64}}) -->", issue["body"])
        if old is None:
            raise ValueError("tracking issue has invalid state")
        if old[1] == digest:
            return "unchanged"
        number = str(issue["number"])
        if issue["state"] == "CLOSED":
            gh("issue", "reopen", number)
        # Comment first: if notification fails, do not mark the transition handled.
        path.write_text("Vulnerability gate state changed.\n\n" + body)
        gh("issue", "comment", number, "--body-file", str(path))
        path.write_text(body)
        gh("issue", "edit", number, "--body-file", str(path))
        return "updated and notified"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run_url = (f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/"
               f"{os.environ['GITHUB_RUN_ID']}")
    if args.dry_run:
        print(issue_body(args.reports, run_url)[1])
    else:
        print(publish(args.reports, run_url))


if __name__ == "__main__":
    main()
