# Continuous integration

CI runs repository validation, configuration scanning, native AMD64 and ARM64
image builds, restricted-runtime smoke tests, Trivy and Grype vulnerability
gates, and Syft SPDX SBOM generation. Runtime tests cover authentication and
configuration precedence, initialization failure modes, durable-state
lifecycle and crash recovery, logical backup/restoration, and the TLS profile.
Resource tests exercise inode, shared-memory, connection, and cgroup-memory
exhaustion under explicit file-descriptor and PID ceilings, then validate
durable-data recovery.
The aggregate `image` job fails unless
every native image job succeeds. Each image job acquires the architecture's
committed lock, verifies the bundle and full key fingerprints, pre-pulls only
the digest-pinned bases, and performs a clean build with network access and
additional pulls disabled.

## Local repository checks

```console
python -m pip install --require-hashes --only-binary=:all: \
  --requirement .github/requirements/pre-commit.txt
pre-commit run --all-files --show-diff-on-failure
```

## Local image checks

```console
CONTAINER_RUNTIME=podman IMAGE=localhost/postgresql-ubi:development \
  bash scripts/build-offline.sh
CONTAINER_RUNTIME=podman IMAGE=localhost/postgresql-ubi:development \
  bash tests/smoke.sh
```

Local success is development evidence, not native multi-architecture or
release evidence. Review workflow logs, warnings, skipped steps, scanner
results, and retained artifacts rather than relying only on a green aggregate
status.

## Release pipeline

The tag-only pipeline validates immutable identity, builds and tests native OCI
candidates, scans before and after publication, requires `release` environment
approval, publishes the two-tag AMD64/ARM64 index, attaches keyless Cosign
evidence, verifies it, and only then creates a GitHub Release. Permissions,
evidence, failure handling, and consumer commands are in
[RELEASE.md](RELEASE.md). It cannot publish a supported image until Package 8
completes the disposable rehearsal, settings audit, frozen qualification, and
independent approval.

## Evidence boundary

CI artifacts contain exact-commit SBOM and scan results and expire after 14
days. Release transfer archives expire after 7 days and release workflow
evidence after 90 days; durable release assets and their required independent
backup follow [the release policy](RELEASE.md#retention-and-backup).
