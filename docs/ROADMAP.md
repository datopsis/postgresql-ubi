# First-release roadmap

This is the release gate for the first supported `postgresql-ubi` image.

## Package 1: project contract

- [x] Define repository, image, versioning, support, contribution, and security
  contracts.
- [x] Add pinned repository checks and baseline GitHub automation.
- [x] Select PGDG PostgreSQL 18 RPMs after verifying the public UBI limitation.

## Package 2: development image

- [x] Add a digest-pinned UBI Minimal builder and UBI Micro runtime.
- [x] Add a non-root entrypoint with mandatory initialization credentials and
  SCRAM network authentication.
- [x] Add a restricted Compose service and stateful smoke tests.
- [ ] Replace build-time repository resolution with an architecture-specific
  artifact lock, verified acquisition, and network-disabled assembly.

## Package 3: release assurance

- [ ] Qualify native AMD64 and ARM64 builds and runtime tests.
- [ ] Review complete SBOM and Trivy/Grype findings with PGDG and Red Hat
  advisory context.
- [ ] Add release-tag validation, keyless signing, provenance, attestations,
  immutable GHCR publication, and release verification.
- [ ] Define supported update cadence, supersession, and vulnerability SLAs.

## Package 4: platform qualification

- [ ] Qualify a documented rootless Podman and Linux host baseline.
- [ ] Qualify Docker compatibility independently.
- [ ] Test OpenShift restricted-SCC arbitrary-UID operation.
- [ ] Add backup/restore, TLS, logging, storage, and major-upgrade guidance.
