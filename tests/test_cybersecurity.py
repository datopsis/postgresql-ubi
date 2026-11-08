import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

import jsonschema


SCRIPT = Path(__file__).parents[1] / "scripts" / "cybersecurity.py"
SPEC = importlib.util.spec_from_file_location("cybersecurity", SCRIPT)
assert SPEC and SPEC.loader
CYBER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CYBER)


class CybersecurityTests(unittest.TestCase):
    def test_committed_artifacts_are_valid_and_current(self):
        CYBER.run(check=True, schema_path=None)

    def test_duplicate_control_is_rejected(self):
        document = CYBER.load_json(CYBER.OSCAL)
        requirements = document["component-definition"]["components"][0][
            "control-implementations"
        ][0]["implemented-requirements"]
        requirements.append(requirements[0])
        with self.assertRaisesRegex(CYBER.ValidationError, "more than once"):
            CYBER.control_records(document)

    def test_permanent_exception_is_rejected(self):
        entry = {field: "value" for field in CYBER.EXCEPTION_FIELDS}
        entry.update(
            image_digest="sha256:" + "a" * 64,
            architecture="amd64",
            expires="never",
        )
        with self.assertRaisesRegex(CYBER.ValidationError, "permanent"):
            CYBER.validate_exceptions({"schema_version": 1, "exceptions": [entry]})

    def test_schema_digest_is_enforced_before_parser(self):
        with tempfile.TemporaryDirectory() as directory:
            schema = Path(directory) / "schema.json"
            schema.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(CYBER.ValidationError, "digest mismatch"):
                CYBER.validate_schema({}, schema)

    def test_pending_findings_cannot_carry_approval_or_be_unapproved_exceptions(self):
        document = CYBER.load_json(CYBER.EXCEPTIONS)
        schema = CYBER.load_json(CYBER.ROOT / "compliance/schemas/vulnerability-exception.schema.json")
        jsonschema.Draft202012Validator(schema).validate(document)
        entry = {field: "value" for field in CYBER.EXCEPTION_FIELDS}
        entry.update(image_digest="sha256:" + "a" * 64, architecture="amd64",
                     expires="2026-11-15", approval="")
        document = {"schema_version": 1, "exceptions": [], "pending_findings": [entry]}
        for change in ("forged", "missing", "promoted"):
            with self.subTest(change=change):
                invalid = copy.deepcopy(document)
                if change == "forged":
                    invalid["pending_findings"][0]["approval"] = "Someone approved"
                elif change == "missing":
                    del invalid["pending_findings"][0]["approval"]
                else:
                    invalid["exceptions"].append(invalid["pending_findings"].pop())
                with self.assertRaises(CYBER.ValidationError):
                    CYBER.validate_exceptions(invalid)
                with self.assertRaises(jsonschema.ValidationError):
                    jsonschema.Draft202012Validator(schema).validate(invalid)


if __name__ == "__main__":
    unittest.main()
