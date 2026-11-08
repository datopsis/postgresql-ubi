from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from artifacts import LockError  # noqa: E402

spec = importlib.util.spec_from_file_location("refresh_bases", ROOT / "scripts/refresh-bases.py")
refresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refresh)


class BaseIndexTests(unittest.TestCase):
    def setUp(self):
        self.index = {
            "schemaVersion": 2,
            "mediaType": refresh.INDEX_TYPES[0],
            "manifests": [
                {"platform": {"os": "linux", "architecture": arch}, "digest": "sha256:" + "a" * 64}
                for arch in ("amd64", "arm64")
            ],
        }

    def verify(self, index):
        raw = json.dumps(index).encode()
        return refresh.verify_index(raw, "sha256:" + hashlib.sha256(raw).hexdigest())

    def test_accepts_both_index_formats(self):
        for media_type in refresh.INDEX_TYPES:
            self.index["mediaType"] = media_type
            self.verify(self.index)

    def test_rejects_missing_duplicate_or_non_linux_platform(self):
        for change in ("missing", "duplicate", "windows", "invalid_digest"):
            with self.subTest(change=change):
                index = copy.deepcopy(self.index)
                if change == "missing":
                    index["manifests"].pop()
                elif change == "duplicate":
                    index["manifests"].append(index["manifests"][0])
                elif change == "windows":
                    index["manifests"][1]["platform"]["os"] = "windows"
                else:
                    index["manifests"][1]["digest"] = "latest"
                with self.assertRaises(LockError):
                    self.verify(index)

    def test_rejects_tampered_bytes_and_single_arch_manifest(self):
        with self.assertRaises(LockError):
            refresh.verify_index(json.dumps(self.index).encode(), "sha256:" + "0" * 64)
        self.index["mediaType"] = "application/vnd.oci.image.manifest.v1+json"
        with self.assertRaises(LockError):
            self.verify(self.index)


class RenderUpdateTests(unittest.TestCase):
    def test_noop_is_byte_identical_but_base_change_gets_new_timestamp(self):
        # Replay actual native inventory metadata through the production renderer.
        for arch in ("amd64", "arm64"):
            with self.subTest(arch=arch), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                original = (ROOT / f"artifacts/locks/{arch}.json").read_bytes()
                lock = json.loads(original)
                inputs = json.loads((ROOT / "artifacts/lock-inputs.json").read_text())
                inputs["base_images"] = {role: value["reference"] for role, value in lock["base_images"].items()}
                (root / "inputs.json").write_text(json.dumps(inputs))
                (root / "lock.json").write_bytes(original)
                binary = []
                for p in lock["packages"]:
                    binary.append("\t".join(str(value) for value in (
                        p["filename"], p["name"], p["epoch"], p["version"], p["release"],
                        p["architecture"], p["source_rpm"], p["signing_key_fingerprint"][-16:],
                        p["repository"], p["url"], p["size"], p["sha256"],
                    )))
                (root / "binary.tsv").write_text("\n".join(binary) + "\n")
                source = ["\t".join(str(p[k]) for k in ("filename", "repository", "url", "size", "sha256"))
                          for p in lock["source_packages"]]
                (root / "source.tsv").write_text("\n".join(source) + "\n")
                command = [sys.executable, str(ROOT / "scripts/render-lock.py"),
                           "--inputs", str(root / "inputs.json"), "--architecture", arch,
                           "--binary-inventory", str(root / "binary.tsv"),
                           "--source-inventory", str(root / "source.tsv"),
                           "--output", str(root / "lock.json")]
                subprocess.run(command, check=True)
                self.assertEqual((root / "lock.json").read_bytes(), original)
                inputs["base_images"]["runtime"] = inputs["base_images"]["runtime"].split("@")[0] + "@sha256:" + "c" * 64
                (root / "inputs.json").write_text(json.dumps(inputs))
                lock["generated_at"] = "2000-01-01T00:00:00Z"
                (root / "lock.json").write_text(json.dumps(lock))
                subprocess.run(command, check=True)
                result = json.loads((root / "lock.json").read_text())
                self.assertNotEqual(result["generated_at"], lock["generated_at"])
                self.assertEqual(result["base_images"]["runtime"]["reference"], inputs["base_images"]["runtime"])


class ProposalTests(unittest.TestCase):
    def test_noop_does_not_publish_and_change_pushes_then_opens_pr_and_dispatches(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            repo.mkdir()
            remote = root / "remote.git"

            def git(*args, cwd=repo):
                return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)

            git("init", "--bare", str(remote))
            git("init", "-b", "main")
            git("config", "user.name", "Test")
            git("config", "user.email", "test@example.invalid")
            for name in ("scripts", "artifacts"):
                shutil.copytree(ROOT / name, repo / name)
            shutil.copy(ROOT / "Containerfile", repo)
            # Fixture bases can differ during an in-progress local update.
            inputs = json.loads((repo / "artifacts/lock-inputs.json").read_text())
            for arch in ("amd64", "arm64"):
                path = repo / f"artifacts/locks/{arch}.json"
                lock = json.loads(path.read_text())
                for role, reference in inputs["base_images"].items():
                    lock["base_images"][role].update(reference=reference, digest=reference.split("@")[1])
                path.write_text(json.dumps(lock))
            git("add", ".")
            git("commit", "-m", "test: initial inputs")
            git("remote", "add", "origin", str(remote))
            git("push", "-u", "origin", "main")
            bin_dir = root / "bin"
            bin_dir.mkdir()
            gh = bin_dir / "gh"
            gh.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$GH_TEST_LOG"\n')
            gh.chmod(0o755)
            (bin_dir / "python").symlink_to(sys.executable)
            log = root / "gh.log"
            env = dict(os.environ, PATH=f"{bin_dir}:{os.environ['PATH']}",
                       GH_TEST_LOG=str(log), GITHUB_RUN_ID="123", GITHUB_RUN_ATTEMPT="1")
            command = ["bash", "scripts/propose-lock-update.sh"]
            subprocess.run(command, cwd=repo, env=env, check=True, capture_output=True)
            self.assertFalse(log.exists())
            with (repo / "Containerfile").open("a") as handle:
                handle.write("\n# Updated candidate\n")
            subprocess.run(command, cwd=repo, env=env, check=True, capture_output=True)
            calls = log.read_text().splitlines()
            self.assertEqual(calls[0], "auth setup-git")
            self.assertTrue(calls[1].startswith("pr create --base main --head automation/artifact-locks-123-1"))
            self.assertEqual(calls[2], "workflow run ci.yml --ref automation/artifact-locks-123-1")
            self.assertEqual(git("rev-parse", "HEAD").stdout,
                             git("rev-parse", "refs/heads/automation/artifact-locks-123-1", cwd=remote).stdout)


if __name__ == "__main__":
    unittest.main()
