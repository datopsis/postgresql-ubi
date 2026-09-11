# Changelog

All notable changes to this project are recorded in this file.

The project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
but container releases use the upstream-derived format documented in
`docs/VERSION.md` rather than Semantic Versioning.

## [Unreleased]

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
