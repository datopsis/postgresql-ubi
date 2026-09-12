import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/release.yml"


class ReleaseWorkflowPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = WORKFLOW.read_text(encoding="utf-8")

    def test_third_party_actions_are_immutable(self):
        uses = re.findall(r"^\s*uses:\s*([^\s#]+)", self.content, re.MULTILINE)
        self.assertGreater(len(uses), 0)
        for reference in uses:
            with self.subTest(reference=reference):
                self.assertRegex(reference, r"^[^@]+@[0-9a-f]{40}$")

    def test_release_cannot_be_cancelled_or_run_from_pull_request(self):
        self.assertIn("cancel-in-progress: false", self.content)
        self.assertNotIn("pull_request_target:", self.content)
        self.assertNotIn("pull_request:", self.content)
        self.assertNotIn("workflow_dispatch:", self.content)

    def test_approval_scanning_oidc_and_release_are_separate(self):
        self.assertIn("environment: release", self.content)
        self.assertEqual(self.content.count("id-token: write"), 1)
        self.assertIn("name: scan published digest", self.content)
        self.assertIn("name: attest, sign, and independently verify", self.content)
        self.assertIn("name: publish durable release evidence", self.content)

    def test_no_mutable_consumer_tags_or_release_cache(self):
        self.assertNotRegex(self.content, r"type=raw,value=(latest|18|18[.]6)")
        self.assertNotIn("cache-from:", self.content)
        self.assertNotIn("cache-to:", self.content)
        self.assertIn('${IMAGE}:${RELEASE_TAG}', self.content)
        self.assertIn('${IMAGE}:${COMMIT_TAG}', self.content)

    def test_missing_evidence_is_fatal(self):
        self.assertGreaterEqual(self.content.count("if-no-files-found: error"), 4)
        self.assertNotIn("continue-on-error: true", self.content)


if __name__ == "__main__":
    unittest.main()
