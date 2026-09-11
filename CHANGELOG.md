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

