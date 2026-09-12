# Cryptographic boundary and claims

There is no FIPS 140 validation claim for `postgresql-ubi`. UBI/RHEL origin,
host FIPS mode, TLS 1.2/1.3 support, SCRAM-SHA-256, checksums, SHA-256 artifact
hashes, or Cosign signatures do not by themselves establish that PostgreSQL or
the image is operating inside a validated cryptographic module boundary.

## Separate mechanisms and owners

| Mechanism | Boundary and purpose | Evidence needed before a claim | Owner |
| --- | --- | --- | --- |
| PostgreSQL SCRAM-SHA-256 | PostgreSQL client/server authentication and verifier in `PGDATA`; not data-at-rest encryption. | Exact server/client builds, linked crypto behavior, configured method/iterations, stored verifier migration, protocol tests. | Image supports; database owner configures. |
| PostgreSQL TLS | Server executable, linked OpenSSL libraries/providers, key/certificate files, client library/trust, DNS and time. | `ldd`/package inventory per architecture, provider and mode output, effective TLS settings, client verification tests, applicable CMVP certificate/boundary. | Image, deployment, PKI, client and host share. |
| PostgreSQL data checksums | PostgreSQL page-corruption detection inside a cluster; not encryption, signatures, or malicious-tamper prevention. | Initialization state, `pg_controldata`, corruption detection and recovery procedure. | Database/storage owner. |
| Build hashes and RPM signatures | Acquisition workstation/runner, RPM verification tools, pinned publisher keys, lock files. | Tool/package versions, key fingerprints, source/binary mapping, negative verification tests. | Maintainer. |
| Release signing/attestation | GitHub OIDC identity, Cosign/Rekor services, workflow and GHCR digest. Protects artifact identity, not database cryptographic operations. | Signed immutable digest, bundle, identity/issuer policy and independent verification. | Maintainer/platform providers. |
| Host/runtime cryptography | Host kernel crypto state, OpenSSL policy/providers, runtime, storage/network encryption and hardware. | Exact qualified host/runtime, boot state, policies, modules, architecture and deployment test evidence. | Host/platform organization. |

The locked package manifests and SBOM identify installed OpenSSL and PostgreSQL
packages. CI must also retain `ldd` output for `postgres`, `openssl version` or
provider inventory where the executable exists, PostgreSQL build configuration,
architecture, and the image digest. A package name is not proof that a process
loaded a module or ran in an approved mode.

## Claim gate

A future cryptographic or FIPS claim requires a security reviewer to identify
the exact library/module and version, module boundary, architecture, provider
configuration, operational environment, algorithms/services used, applicable
non-expired CMVP certificate, and correspondence between that certificate and
the shipped binary. The reviewer must test approved and failure modes on the
exact release digest and supported host profile. Any library, provider,
PostgreSQL, base image, host mode, architecture, build flag, or certificate
change invalidates that evidence.

Until that work is complete, SC-13 is `research-required`, and deployments must
make their own authorization decision without citing this project as FIPS
validated.
