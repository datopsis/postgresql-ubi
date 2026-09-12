import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY / "scripts" / "release.py"
GOOD_TAG = "v18.6-ubi9-r20260911.1"


class ReleaseTagTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=REPOSITORY)
        self.root = Path(self.temporary.name)
        (self.root / "artifacts/locks").mkdir(parents=True)
        (self.root / "Containerfile").write_text(
            '\n'.join(
                [
                    'ARG UBI_MINIMAL_IMAGE="registry/ubi9/minimal:9.8@sha256:' + 'a' * 64 + '"',
                    'ARG UBI_MICRO_IMAGE="registry/ubi9/micro:9.8@sha256:' + 'b' * 64 + '"',
                    'ARG POSTGRESQL_VERSION="18.6"',
                    'ARG POSTGRESQL_RPM_VERSION="18.6-1PGDG.rhel9.8"',
                ]
            ) + '\n',
            encoding="utf-8",
        )
        bases = {
            "builder": "registry/ubi9/minimal:9.8@sha256:" + "a" * 64,
            "runtime": "registry/ubi9/micro:9.8@sha256:" + "b" * 64,
        }
        inputs = {
            "postgresql_version": "18.6",
            "postgresql_rpm_version": "18.6-1PGDG.rhel9.8",
            "ubi_release": "9.8",
            "base_images": bases,
        }
        self.write_json("artifacts/lock-inputs.json", inputs)
        for architecture in ("amd64", "arm64"):
            lock_bases = {
                name: {
                    "reference": reference,
                    "digest": reference.rsplit("@", 1)[1],
                }
                for name, reference in bases.items()
            }
            self.write_json(
                f"artifacts/locks/{architecture}.json",
                {
                    "architecture": architecture,
                    "postgresql_version": "18.6",
                    "postgresql_rpm_version": "18.6-1PGDG.rhel9.8",
                    "base_images": lock_bases,
                },
            )
        (self.root / "CHANGELOG.md").write_text(
            f"# Changelog\n\n## [Unreleased]\n\n## [{GOOD_TAG}] - 2026-09-11\n",
            encoding="utf-8",
        )
        self.git("init", "--quiet")
        self.git("config", "user.name", "Release test")
        self.git("config", "user.email", "release@example.invalid")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "fixture")
        self.git("tag", "--annotate", GOOD_TAG, "--message", "fixture release")

    def tearDown(self):
        self.temporary.cleanup()

    def write_json(self, relative: str, value: dict):
        (self.root / relative).write_text(json.dumps(value), encoding="utf-8")

    def git(self, *args: str):
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def validate(self, tag=GOOD_TAG, *options, environment=None):
        env = os.environ.copy()
        if environment:
            env.update(environment)
        return subprocess.run(
            [sys.executable, os.fspath(SCRIPT), tag, "--root", os.fspath(self.root), *options],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )

    def assert_rejected(self, tag=GOOD_TAG, *options, environment=None):
        self.assertNotEqual(
            self.validate(tag, *options, environment=environment).returncode, 0
        )

    def test_accepts_complete_matching_annotated_candidate(self):
        result = self.validate(
            GOOD_TAG,
            "--require-annotated",
            "--require-current-date",
            "--require-next-sequence",
            environment={"RELEASE_DATE_UTC": "20260911"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["commit_tag"].split("-")[0], "sha")

    def test_rejects_malformed_mutable_and_impossible_dates(self):
        for tag in (
            "latest",
            "18",
            "v18.6-ubi9-r20260230.1",
            "v18.6-ubi9-r20260911.0",
            "v18.6-ubi9-r20260911.01",
        ):
            with self.subTest(tag=tag):
                self.assert_rejected(tag)

    def test_rejects_version_ubi_lock_and_changelog_mismatches(self):
        for tag in (
            "v18.7-ubi9-r20260911.1",
            "v18.6-ubi10-r20260911.1",
            "v18.6-ubi9-r20260912.1",
        ):
            with self.subTest(tag=tag):
                self.assert_rejected(tag)
        lock = json.loads((self.root / "artifacts/locks/arm64.json").read_text())
        lock["postgresql_version"] = "18.5"
        self.write_json("artifacts/locks/arm64.json", lock)
        self.assert_rejected()

    def test_rejects_lightweight_tag_wrong_commit_and_moved_tag(self):
        self.git("tag", "--delete", GOOD_TAG)
        self.git("tag", GOOD_TAG)
        self.assert_rejected(GOOD_TAG, "--require-annotated")
        self.git("tag", "--delete", GOOD_TAG)
        self.git("tag", "--annotate", GOOD_TAG, "--message", "moved")
        self.assert_rejected(
            GOOD_TAG,
            "--require-annotated",
            environment={"GITHUB_SHA": "0" * 40},
        )

    def test_rejects_reused_daily_sequence(self):
        second = "v18.6-ubi9-r20260911.2"
        self.git("tag", "--annotate", second, "--message", "second")
        self.assert_rejected(GOOD_TAG, "--require-next-sequence")


if __name__ == "__main__":
    unittest.main()
