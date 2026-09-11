# Repository guidance

## Project overview

This repository builds a security-oriented, rootless PostgreSQL 18 container
on Red Hat UBI 9 Micro. Preserve these non-negotiable properties:

- digest-pinned UBI base images and exact PostgreSQL build inputs;
- a package-manager-free final runtime;
- non-root PostgreSQL execution with no privilege transition;
- authenticated network access using SCRAM by default;
- no generated, default, or logged database passwords;
- a persistent, explicitly writable data volume with a read-only root
  filesystem;
- no Linux capabilities and `no-new-privileges` in documented deployments;
- graceful shutdown and persistent-data restart tests;
- native AMD64 and ARM64 CI, SBOMs, vulnerability scans, and signed immutable
  releases; and
- no support, FIPS, STIG, or platform claims without matching evidence.

The release rules are in `docs/VERSION.md`. Package-source and forward-looking
work are defined in `docs/PACKAGE-SOURCE.md` and `docs/ROADMAP.md`.

## Development and verification

Use Podman for the primary local workflow. For image-affecting work, verify at
least initialization, authenticated SQL, data persistence across replacement,
clean shutdown, non-root execution, read-only-root behavior, zero capabilities,
`no-new-privileges`, and failure without initialization credentials.

Never commit generated databases, passwords, private keys, SBOMs, SARIF, or
scanner caches.

## Git conventions

Keep changes small and reviewable. Use protected `main`, required checks, and
pull requests. Do not force-push or move release tags. Use concise Conventional
Commit subjects. Do not add AI, assistant, tool-attribution, or
`Co-Authored-By` trailers.
