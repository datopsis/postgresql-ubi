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

## Evidence boundary

CI artifacts contain exact-commit SBOM and scan results and currently expire
after 14 days. Release evidence requirements, retention, signing, provenance,
and publication remain first-release roadmap work.
