# External artifact acquisition

Status: required for the first release. The development `Containerfile`
currently resolves an exact RPM version during its builder stage and must be
migrated before release.

## Build contract

Ordinary pull-request, `main`, and release assembly must not resolve mutable
package metadata or download packages, keys, or repository configuration from
inside the container build. A separate preparation phase acquires and verifies
every input. Assembly then runs with network access and image pulling disabled.

The pipeline separates:

1. **Resolution**, performed only by an explicit lock-update operation.
2. **Acquisition**, which downloads only artifacts already named by the lock.
3. **Verification**, which checks publisher identity and exact bytes.
4. **Assembly**, which consumes only the verified local bundle.

## Required lock contents

The architecture-specific lock records:

- each UBI base reference and expected manifest digest;
- the PGDG repository-package identity and checksum;
- every PostgreSQL and UBI RPM NEVRA, byte size, and SHA-256 digest;
- expected architecture and RPM signing fingerprint;
- source-RPM locations and digests;
- artifact-source identifier; and
- lock schema and artifact-bundle version.

The lock is reviewable repository content. Credentials, tokens, private
endpoints, and private trust material are not.

## Verification requirements

Before assembly, CI must:

- reject missing, additional, duplicate, wrong-architecture, or wrong-version
  files;
- verify every artifact's size and SHA-256 digest;
- verify RPM signatures against approved full fingerprints;
- verify package NEVRA and source-RPM correspondence;
- verify base-image platform and manifest digest;
- sanitize acquisition logs; and
- retain the lock digest and verification result with release evidence.

Checksums prove exact bytes; signatures prove publisher authorization under the
accepted key policy. TLS transport does not replace either check.

## Network-disabled assembly

The verified RPM bundle is supplied as an ephemeral build context excluded from
Git. The Containerfile installs it into a temporary root and copies only the
required runtime filesystem into UBI Micro. Assembly must prove:

- no network access and no image pulling;
- no dependency resolution;
- no repository credentials, configuration, keys, or caches in image layers,
  history, labels, SBOM, or provenance; and
- failure for any incomplete or unverified bundle.

Changing any locked package, base digest, acquisition tool, or verification
policy invalidates earlier release-candidate evidence.

## Current development limitation

The current Containerfile checksum-pins the three PostgreSQL 18.6 RPMs and the
PGDG signing key, then verifies the RPM signatures. The builder still resolves
the UBI dependency closure over the network. This supports early runtime
development but is not release-qualified or fully reproducible if UBI metadata
or packages change. No image produced by that path may be announced as
supported.
