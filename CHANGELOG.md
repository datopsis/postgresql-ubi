# Changelog

All notable changes to this project are recorded in this file.

The project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
but container releases use the upstream-derived format documented in
`docs/VERSION.md` rather than Semantic Versioning.

## [Unreleased]

### Fixed

- Update PostgreSQL to 18.7 with native PGDG builds `1PGDG.rhel9.9` (AMD64)
  and `2PGDG.rhel9.9` (ARM64), regenerated NEVRA/SHA-256 binary/source locks,
  and a refreshed UBI RPM closure. Preserve offline acquisition/assembly and
  all vulnerability and runtime checks. Record architecture-specific RPM
  releases in image labels and explain disappearing upstream URLs in CI docs.
  [PostgreSQL 18.7 release notes](https://www.postgresql.org/docs/release/18.7/)
  list these security fixes:
  CVE-2026-116303, CVE-2026-116304, CVE-2026-116306, CVE-2026-116307,
  CVE-2026-116308, CVE-2026-116309, CVE-2026-116310, CVE-2026-116311,
  CVE-2026-116312, CVE-2026-116313, CVE-2026-116314, CVE-2026-116315,
  CVE-2026-116316, CVE-2026-116317, CVE-2026-116318, CVE-2026-116319,
  CVE-2026-116320, CVE-2026-116321, CVE-2026-116322, CVE-2026-116323,
  CVE-2026-116325, CVE-2026-116326, CVE-2026-116327, CVE-2026-116328,
  CVE-2026-116329, CVE-2026-116330, CVE-2026-116331, CVE-2026-116332,
  CVE-2026-116333, CVE-2026-116335, CVE-2026-116336, CVE-2026-120139,
  CVE-2026-120141, CVE-2026-120142, CVE-2026-120143, CVE-2026-120144,
  CVE-2026-120145, CVE-2026-120146, CVE-2026-120147, CVE-2026-120148,
  CVE-2026-120149, CVE-2026-120150, CVE-2026-120151, CVE-2026-120152,
  CVE-2026-120153, CVE-2026-120154, CVE-2026-14661, CVE-2026-16237,
  CVE-2026-16240, CVE-2026-18447, CVE-2026-6460, CVE-2026-6464,
  CVE-2026-6467.

- Create the application database when `POSTGRES_DB` defaults to or equals
  `POSTGRES_USER`, owned by that role. Reuse `postgres`, reject template names
  before initialization, and retain existing-data restart behavior. Cover
  initialization and restart cases in native AMD64 and ARM64 smoke tests.

- Regenerated both native RPM/source locks and refreshed the selected UBI base
  digests. Updated the util-linux family to 2.37.4-28.el9_9.1, expat to
  2.5.0-9.el9_9.4, and libxml2 to 2.9.13-18.el9_9.1, retaining PostgreSQL 18.6
  and the installable-fix gate.

- Gate vendor-fixed High/Critical UBI RPM findings on native repository
  availability using the pinned builder configuration and RPM version ordering.
  Fail closed on uncertainty and retain ordinary blocking for non-UBI findings.
  Report unavailable fixes in CI/release evidence and a daily tracking issue
  that notifies subscribers when availability or findings change.

- Regenerated the CI tool requirements with complete version pins and wheel
  hashes, including virtualenv's packaging dependency, while retaining
  filelock 3.x. Added inputs and commands for repeatable regeneration.

### Added

- Established the `postgresql-ubi` repository and planned GHCR image identity.
- Selected PostgreSQL 18 as the maintained major line and 18.6 as the initial
  build target on UBI 9.
- Adapted the `nginx-ubi` immutable container versioning policy for PostgreSQL.
- Added the repository governance, contribution, security, issue, dependency,
  and pinned local-check foundations used by the `nginx-ubi` project.
- Added least-privilege CI, CodeQL, OpenSSF Scorecard, native AMD64 and ARM64
  image tests, vulnerability scanning, and SPDX SBOM generation.
- Documented the PGDG package-source decision after confirming that public UBI
  9.8 repositories do not expose PostgreSQL 18.
- Added a UBI Micro development image, secure initialization entrypoint,
  restricted Compose service, and stateful rootless smoke tests.
- Replaced PGDG repository resolution with checksum-pinned, signature-checked
  PostgreSQL RPM artifacts after native ARM64 exposed invalid signed metadata.
- Pinned the distinct PGDG ARM64 signing key used by the AArch64 RPM artifacts.
- Moved the local PostgreSQL socket to the restricted `/tmp` tmpfs so arbitrary
  non-root users behave consistently under Docker and Podman.
- Directed PostgreSQL logs to container output and made readiness probes use the
  absolute client path and a real SQL query for consistent engine behavior.
- Approved the first-release support boundary and added explicit support
  classifications, lifecycle, update cadence, vulnerability-response targets,
  withdrawal handling, and accountable ownership.
- Added the release qualification evidence schema and a public-badge policy
  that prohibits unsupported security, platform, or certification claims.
- Added schema-defined AMD64 and ARM64 artifact locks for the complete runtime
  RPM and source closure, fail-closed acquisition and publisher verification,
  a manual lock-update workflow, and network-disabled offline assembly.
- Added the PostgreSQL authentication, initialization, immutable configuration,
  storage, crash-recovery, backup/restore, minor-update, TLS, resource-limit,
  logging, and probe runtime contract with native architecture tests.
- Added executable deployment guidance for fixed and arbitrary identities,
  Podman, Docker and Compose, named and bind-mounted storage, TLS and isolated
  non-TLS networks, controlled transfer, operations, recovery, and teardown.
- Added the immutable, least-privilege native release pipeline; fail-closed tag
  policy; digest-bound SBOM, provenance, scanning, signing, verification, and
  evidence controls; upstream monitoring; emergency rebuild; and quarantine
  procedures.
- Added the Package 5 cybersecurity engineering set: authoritative source
  register, schema-validated OSCAL component definition, generated control
  views, architecture and threat model, report-only native SCAP discovery,
  cryptographic claim gate, vulnerability exceptions, incident response, and
  inherited deployment responsibility matrix.
