# External artifact acquisition

Status: implemented and enforced in ordinary CI assembly. Release publication
and durable release-evidence retention remain later roadmap work.

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

## Commands and review flow

`artifacts/lock-inputs.json` is the small, human-reviewed selection. The manual
**Propose artifact lock update** workflow resolves both native closures and
retains candidate locks and inventories; it never commits, merges, or publishes
them. A maintainer compares package and source changes, supplier advisories,
licenses, architecture differences, and base digests before replacing
`artifacts/locks/amd64.json` and `artifacts/locks/arm64.json` through a pull
request.

Ordinary native assembly uses:

```console
CONTAINER_RUNTIME=podman IMAGE=localhost/postgresql-ubi:development \
  bash scripts/build-offline.sh
```

The command requires an absent `.artifact-bundle/<architecture>` destination;
it will not reuse or overwrite a partially acquired directory. The acquirer
permits HTTPS only, rejects credentials, queries, fragments, and redirects to
unapproved hosts, uses bounded timeouts and retries, checks exact size and
SHA-256 while streaming, and atomically admits a complete bundle. The current
public allowlist is `download.postgresql.org`, `dnf-srpms.postgresql.org`,
`cdn-ubi.redhat.com`, and `security.access.redhat.com`.

GnuPG verifies each downloaded key's full fingerprint. An isolated RPM database
then verifies every RPM signature and confirms signer, NEVRA, architecture, and
source-RPM metadata against the bundle manifest. The build re-verifies the lock
digest, signatures, and RPM metadata before installing all RPMs in one offline
transaction. CI pre-pulls and architecture-checks the digest-pinned bases, then
uses `--network=none`, disables pulls, and disables build caching. Unit and
integration checks reject malformed locks, wrong versions or architectures,
unapproved sources or keys, duplicates, missing or extra files, modified
manifests, and byte tampering.

The initial closure review records 161 binary RPMs on AMD64 and 162 on ARM64,
with 111 distinct source RPMs on each. ARM64's only package-name addition is
`libatomic`, an architecture-specific runtime dependency; AMD64 has no unique
package. Locked binary download sizes are 76,382,789 bytes on AMD64 and
74,714,685 bytes on ARM64. Finalization removes every setuid/setgid bit and
fails on any world-writable regular file. CI repeats those assertions while
native smoke, SBOM, and vulnerability jobs inspect the resulting executable
and package content. Future lock updates must explain changes to these counts,
package-name differences, privilege bits, writable files, or executables in the
pull-request review.

## Trust and recovery procedures

- **Key rotation:** stop lock updates, obtain the publisher's new fingerprint
  through an authoritative channel independent of the package download, add the
  exact key URL, hash, and full fingerprint to the reviewed input, and accept it
  only after both native candidate closures verify. Remove an old key only when
  no locked RPM depends on it.
- **Revocation or compromise:** block builds and releases using the affected
  key, preserve evidence, assess every signed package and released digest,
  withdraw affected releases when integrity cannot be established, and require
  replacement publisher-signed artifacts and full requalification. A checksum
  match does not override a revoked signing identity.
- **Mirror substitution:** change both the source allowlist and lock URLs in a
  reviewed security change. The mirror must serve byte-identical,
  publisher-signed files. Any re-signing requires a separately documented and
  approved trust boundary.
- **Bundle transfer:** archive the complete architecture directory without
  modification, transfer it over the deployment organization's approved
  channel, and run `verify-bundle`, full fingerprint verification, and RPM
  verification at the receiving boundary before assembly. Do not transfer
  credentials, repository configuration, or caches with it.
- **Rollback:** restore a previously committed lock and its exact bundle only
  through a pull request, confirm all bytes and base digests remain available,
  rerun current security gates, and issue a new immutable release identity.
  Never move a tag or reuse previous qualification evidence.
- **Emergency rebuild:** security urgency shortens review latency but does not
  disable signatures, hashes, native builds, vulnerability gates, or immutable
  release identity. If trusted inputs or required evidence are unavailable,
  delay or withdraw the release and publish mitigation rather than bypassing a
  control.

## Source, redistribution, and ownership

Every binary lock entry names its source RPM, and every distinct source RPM has
an HTTPS location, repository identifier, byte size, and SHA-256 record. PGDG
PostgreSQL packages remain under the PostgreSQL License; UBI base content and
runtime dependencies remain under Red Hat's UBI terms and their included
per-package licenses. The image and repository names do not imply PostgreSQL or
Red Hat endorsement, certification, or support. `THIRD_PARTY_NOTICES.md`
records the redistribution boundary, and `docs/MAINTENANCE.md` assigns weekly
supplier, source, license, signing-key, and update review to the accountable
maintainer.
