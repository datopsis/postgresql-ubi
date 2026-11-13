import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import track_vulnerabilities as tracker


class TrackingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for arch in ("amd64", "arm64"):
            directory = self.root / f"vulnerability-gate-{arch}"
            directory.mkdir()
            (directory / "gate.json").write_text(json.dumps(dict(
                architecture=arch, findings=[], errors=[], checked_at="earlier")))

    def test_missing_report_is_visible_failure(self):
        (self.root / "vulnerability-gate-arm64/gate.json").unlink()
        self.assertIn("missing or ambiguous", tracker.issue_body(self.root, "run")[1])

    def test_timestamp_and_run_do_not_notify(self):
        digest, body = tracker.issue_body(self.root, "old-run")
        for path in self.root.glob("*/gate.json"):
            data = json.loads(path.read_text())
            data["checked_at"] = "later"
            path.write_text(json.dumps(data))
        self.assertEqual(digest, tracker.issue_body(self.root, "new-run")[0])
        with patch.object(tracker, "gh", return_value=json.dumps([
                dict(number=1, title=tracker.TITLE, body=body, state="OPEN")])) as gh:
            self.assertEqual(tracker.publish(self.root, "new-run"), "unchanged")
            self.assertEqual(gh.call_count, 1)

    def test_state_change_comments_and_updates_same_issue(self):
        _, body = tracker.issue_body(self.root, "old-run")
        path = self.root / "vulnerability-gate-arm64/gate.json"
        data = json.loads(path.read_text())
        data["errors"] = ["query failure"]
        path.write_text(json.dumps(data))
        with patch.object(tracker, "gh", side_effect=[json.dumps([
                dict(number=7, title=tracker.TITLE, body=body, state="OPEN")]), "", ""]) as gh:
            self.assertEqual(tracker.publish(self.root, "run"), "updated and notified")
            self.assertEqual(gh.call_args_list[1].args[:3], ("issue", "comment", "7"))
            self.assertEqual(gh.call_args_list[2].args[:3], ("issue", "edit", "7"))

    def test_deferred_to_available_notifies(self):
        path = self.root / "vulnerability-gate-amd64/gate.json"
        data = json.loads(path.read_text())
        row = dict(scanner="example", id="example-advisory", package="example-rpm",
                   installed="1.0-1", severity="HIGH", fixed=["1.0-2"],
                   decision="deferred", reason="vendor fix not yet available in UBI")
        data["findings"] = [row]
        path.write_text(json.dumps(data))
        _, old_body = tracker.issue_body(self.root, "old-run")
        row.update(decision="blocked", reason="fixed or newer RPM available in UBI")
        path.write_text(json.dumps(data))
        with patch.object(tracker, "gh", side_effect=[json.dumps([
                dict(number=7, title=tracker.TITLE, body=old_body, state="OPEN")]), "", ""]) as gh:
            self.assertEqual(tracker.publish(self.root, "run"), "updated and notified")
            self.assertEqual(gh.call_args_list[1].args[:3], ("issue", "comment", "7"))

    def test_first_run_creates_one_issue(self):
        with patch.object(tracker, "gh", side_effect=["[]", "created"]) as gh:
            self.assertEqual(tracker.publish(self.root, "run"), "created")
            self.assertEqual(gh.call_args_list[1].args[:2], ("issue", "create"))

    def test_notification_failure_does_not_record_transition(self):
        old = f"<!-- {tracker.MARKER}:{'0' * 64} -->"
        with patch.object(tracker, "gh", side_effect=[json.dumps([
                dict(number=7, title=tracker.TITLE, body=old, state="OPEN")]), RuntimeError("API error")]) as gh:
            with self.assertRaises(RuntimeError):
                tracker.publish(self.root, "run")
            self.assertEqual(gh.call_count, 2)


if __name__ == "__main__":
    unittest.main()
