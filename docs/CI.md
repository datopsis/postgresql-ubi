# Continuous integration

CI runs repository validation, configuration scanning, native AMD64 and ARM64
image builds, restricted-runtime smoke tests, Trivy and Grype vulnerability
gates, and Syft SPDX SBOM generation. The aggregate `image` job fails unless
every native image job succeeds.

## Local repository checks

```console
python -m pip install --require-hashes --only-binary=:all: \
  --requirement .github/requirements/pre-commit.txt
pre-commit run --all-files --show-diff-on-failure
```

## Local image checks

```console
podman build --format docker --file Containerfile \
  --tag localhost/postgresql-ubi9:development .
CONTAINER_RUNTIME=podman IMAGE=localhost/postgresql-ubi9:development \
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
