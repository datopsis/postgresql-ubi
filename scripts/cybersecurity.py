#!/usr/bin/env python3
"""Validate Package 5 records and render deterministic control views."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OSCAL = ROOT / "compliance" / "oscal" / "component-definition.json"
SOURCES = ROOT / "compliance" / "source-register.json"
EXCEPTIONS = ROOT / "compliance" / "vulnerability-exceptions.json"
CSV_VIEW = ROOT / "compliance" / "sctm.csv"
MD_VIEW = ROOT / "docs" / "CONTROL-IMPLEMENTATION.md"
NS = "https://datopsis.dev/ns/postgresql-ubi"

CLASSIFICATIONS = {
    "image-owned",
    "deployment-supported",
    "inherited",
    "not-applicable",
    "unsupported",
    "research-required",
}
REQUIRED_PROPS = (
    "classification",
    "source-requirement",
    "rationale",
    "residual-risk",
    "evidence",
    "owner",
    "review-status",
    "assessment-method",
    "default-state",
    "configurable-state",
    "prerequisites",
    "restart-behavior",
    "operational-impact",
    "loss-of-protection",
    "limitations",
)
EXCEPTION_FIELDS = (
    "image_digest",
    "architecture",
    "advisory",
    "component",
    "vendor_status",
    "rationale",
    "compensating_control",
    "owner",
    "approval",
    "expires",
    "rescan_trigger",
)


class ValidationError(ValueError):
    """A Package 5 artifact is invalid."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"{path}: {exc}") from exc


def properties(requirement: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for prop in requirement.get("props", []):
        if prop.get("ns") != NS:
            continue
        name = prop.get("name")
        value = prop.get("value")
        if not isinstance(name, str) or not isinstance(value, str):
            raise ValidationError("control properties must have string name/value")
        if name in result:
            raise ValidationError(
                f"{requirement.get('control-id')}: duplicate property {name}"
            )
        result[name] = value
    return result


def control_records(document: dict[str, Any]) -> list[dict[str, str]]:
    try:
        implementations = document["component-definition"]["components"][0][
            "control-implementations"
        ]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValidationError("missing OSCAL control implementations") from exc

    records: list[dict[str, str]] = []
    seen: set[str] = set()
    for implementation in implementations:
        for requirement in implementation.get("implemented-requirements", []):
            control_id = requirement.get("control-id")
            if not isinstance(control_id, str) or not control_id:
                raise ValidationError("implemented requirement has no control-id")
            if control_id in seen:
                raise ValidationError(f"control classified more than once: {control_id}")
            seen.add(control_id)
            props = properties(requirement)
            missing = [name for name in REQUIRED_PROPS if not props.get(name)]
            if missing:
                raise ValidationError(f"{control_id}: missing {', '.join(missing)}")
            if props["classification"] not in CLASSIFICATIONS:
                raise ValidationError(
                    f"{control_id}: invalid classification {props['classification']}"
                )
            if props["review-status"] not in {
                "reviewed",
                "pending-independent-review",
            }:
                raise ValidationError(f"{control_id}: invalid review status")
            if not props["evidence"].startswith(("docs/", "tests/", ".github/")):
                raise ValidationError(f"{control_id}: evidence must be a repository path")
            records.append(
                {
                    "control_id": control_id,
                    "description": requirement.get("description", ""),
                    **props,
                }
            )
    if not records:
        raise ValidationError("no implemented requirements")
    return sorted(records, key=lambda item: item["control_id"])


def validate_sources(document: Any) -> None:
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        raise ValidationError("source register schema_version must be 1")
    sources = document.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValidationError("source register must contain sources")
    required = {
        "id", "publisher", "title", "release", "publication_date",
        "retrieved", "url", "sha256", "status", "redistribution",
    }
    seen: set[str] = set()
    for source in sources:
        missing = sorted(required - set(source))
        if missing:
            raise ValidationError(f"source missing {', '.join(missing)}")
        if source["id"] in seen:
            raise ValidationError(f"duplicate source id: {source['id']}")
        seen.add(source["id"])
        if not re.fullmatch(r"[0-9a-f]{64}", source["sha256"]):
            raise ValidationError(f"{source['id']}: invalid sha256")
        if source["status"] not in {"current", "superseded", "sunset", "reference"}:
            raise ValidationError(f"{source['id']}: invalid status")


def validate_exceptions(document: Any) -> None:
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        raise ValidationError("exception register schema_version must be 1")
    entries = document.get("exceptions")
    if not isinstance(entries, list):
        raise ValidationError("exceptions must be a list")
    for index, entry in enumerate(entries):
        missing = [field for field in EXCEPTION_FIELDS if not entry.get(field)]
        if missing:
            raise ValidationError(f"exception {index}: missing {', '.join(missing)}")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", entry["image_digest"]):
            raise ValidationError(f"exception {index}: digest must be immutable")
        if entry["architecture"] not in {"amd64", "arm64"}:
            raise ValidationError(f"exception {index}: invalid architecture")
        if entry["expires"] == "never":
            raise ValidationError(f"exception {index}: permanent exceptions are forbidden")


def validate_schema(document: Any, schema_path: Path | None) -> None:
    if schema_path is None:
        return
    digest = hashlib.sha256(schema_path.read_bytes()).hexdigest()
    expected = "95e76881151ececd5cb1a93ff0f70ad74b8cc1aa58771626ac8b262bf2c8e001"
    if digest != expected:
        raise ValidationError(f"OSCAL schema digest mismatch: {digest}")
    try:
        import jsonschema
        import regex
    except ImportError as exc:
        raise ValidationError("jsonschema and regex are required for --oscal-schema") from exc

    def unicode_pattern(validator: Any, pattern: str, instance: Any, schema: Any):
        del validator, schema
        if isinstance(instance, str) and regex.search(pattern, instance) is None:
            yield jsonschema.ValidationError(
                f"{instance!r} does not match OSCAL pattern {pattern!r}"
            )

    oscal_validator = jsonschema.validators.extend(
        jsonschema.Draft7Validator, {"pattern": unicode_pattern}
    )
    oscal_validator(load_json(schema_path)).validate(document)


def render_csv(records: list[dict[str, str]]) -> str:
    fields = ("control_id", "description", *REQUIRED_PROPS)
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows({field: record[field] for field in fields} for record in records)
    return stream.getvalue()


def render_markdown(records: list[dict[str, str]]) -> str:
    lines = [
        "# Control implementation view",
        "",
        "Generated from `compliance/oscal/component-definition.json`; do not edit.",
        "This is component support information, not an SCTM, SSP, authorization,",
        "assessment result, STIG certification, or compliance determination.",
        "",
    ]
    for record in records:
        lines.extend(
            [
                f"## {record['control_id']}: {record['classification']}",
                "",
                record["description"],
                "",
                f"- Source requirement: {record['source-requirement']}",
                f"- Rationale: {record['rationale']}",
                f"- Assessment: {record['assessment-method']}",
                f"- Default/configurable: {record['default-state']} / {record['configurable-state']}",
                f"- Prerequisites/restart: {record['prerequisites']} / {record['restart-behavior']}",
                f"- Operational impact: {record['operational-impact']}",
                f"- Loss of protection: {record['loss-of-protection']}",
                f"- Limitations: {record['limitations']}",
                f"- Residual risk: {record['residual-risk']}",
                f"- Evidence: `{record['evidence']}`",
                f"- Owner/review: {record['owner']} / {record['review-status']}",
                "",
            ]
        )
    return "\n".join(lines)


def write_or_check(path: Path, expected: str, check: bool) -> None:
    if check:
        actual = path.read_text(encoding="utf-8") if path.exists() else ""
        if actual != expected:
            raise ValidationError(f"generated file is stale: {path.relative_to(ROOT)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(expected, encoding="utf-8", newline="")


def run(check: bool, schema_path: Path | None) -> None:
    oscal = load_json(OSCAL)
    records = control_records(oscal)
    validate_sources(load_json(SOURCES))
    validate_exceptions(load_json(EXCEPTIONS))
    validate_schema(oscal, schema_path)
    write_or_check(CSV_VIEW, render_csv(records), check)
    write_or_check(MD_VIEW, render_markdown(records), check)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--oscal-schema", type=Path)
    args = parser.parse_args()
    try:
        run(args.check, args.oscal_schema)
    except (ValidationError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
