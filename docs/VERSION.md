# Versioning and releases

The published container image is versioned independently from repository
history. Git commits identify repository revisions; release versions identify
container artifacts that this project intentionally publishes and supports.

## Supported product line

The initial maintained product line is PostgreSQL 18 on UBI 9. PostgreSQL 18.6
is the initial build target, not a permanently fixed minor line. PostgreSQL's
current minor release for major 18 should replace it after review, rebuild,
testing, and release qualification.

PostgreSQL major upgrades can require `pg_upgrade` or dump and restore. Adding
or changing a maintained major line therefore requires an explicit support,
upgrade, extension-compatibility, and data-compatibility decision. It is not a
routine in-place dependency update.

## Container release format

Annotated Git tags and immutable GHCR image tags use:

```text
v<postgresql-version>-ubi<ubi-major>-r<YYYYMMDD>.<daily-sequence>
```

For example, `v18.6-ubi9-r20260910.1` identifies:

- PostgreSQL 18.6;
- the UBI 9 runtime product line;
- a Datopsis container release created on 2026-09-10 UTC; and
- the first container release created on that UTC date.

The example is illustrative and is not a published or supported release.

The `r` distinguishes a Datopsis container release from an upstream PostgreSQL
release. The eight-digit date is the UTC date on which the immutable release
tag is created. The sequence is a positive integer beginning at `1` and
increments for every additional container release created on the same UTC
date. Dates must not be backdated, and missing or withdrawn sequences must not
be reused.

This upstream-derived format is not Semantic Versioning. The downstream suffix
communicates release chronology and does not make compatibility claims beyond
the documented PostgreSQL and image support contracts.

The tag includes the UBI major because it identifies the runtime product line
and its compatibility boundary. It omits the UBI minor because installed
package updates can make the runtime filesystem newer than the base snapshot.
The exact UBI reference and manifest digest remain required in OCI metadata,
the SBOM, provenance, and release evidence.

Release tags are immutable. Never move or reuse one. A readable tag describes
a release; the OCI digest identifies its exact image content. Production
deployments should pin the digest.

The release workflow must accept only tags matching:

```regex
^v[0-9]+\.[0-9]+-ubi[1-9][0-9]*-r[0-9]{8}\.[1-9][0-9]*$
```

Pattern matching is only the first check. The workflow must also validate a
real UTC date, the locked PostgreSQL version, the locked UBI major, the next
unused sequence for that date, and that the tagged commit is the protected
`main` release commit.

## Artifact identity

OCI metadata records at least:

- `org.opencontainers.image.version` as the complete release identifier without
  the leading `v`;
- `org.opencontainers.image.revision` as the full Git commit SHA;
- `org.opencontainers.image.created` as the reproducible UTC creation time;
- the exact UBI base reference and manifest digest;
- the exact PostgreSQL build-input version, publisher, and verification
  identity; and
- the artifact-lock digest used to prepare build inputs.

The image digest, not a label or tag, is the definitive artifact identity.

## When to create a container release

| Change | Version action |
| --- | --- |
| Update the PostgreSQL minor version within major 18 | Use the new full PostgreSQL version, current UTC date, and next daily sequence. |
| Add or change the PostgreSQL major line | Complete the major-upgrade support decision, then use the selected full PostgreSQL version and a new release identifier. |
| Change the UBI major | Use the new UBI major with the selected PostgreSQL version and a new release identifier. |
| Change only the UBI minor reference or digest | Keep the PostgreSQL and UBI-major fields and create a new release identifier. |
| Change a package, dependency lock, runtime behavior, default configuration, entrypoint, build input, or release metadata | Create a new release identifier. |
| Deliberately rebuild otherwise unchanged inputs | Create a new release identifier. |
| Change only documentation, tests, development tooling, policies, or examples not copied into the image | Do not create a container release unless an image is deliberately republished. |

Every newly published image receives a new immutable release tag.

## Published tags

The first release publishes only:

- the complete immutable release tag, such as
  `v18.6-ubi9-r20260910.1`; and
- an immutable `sha-<short-commit>` traceability tag.

Mutable tags such as `latest`, `18`, or `18.6` are not initially published.
They may be introduced only after their movement, rollback, support, and
consumer-notification behavior is documented. Controlled deployments use an
image digest.

## Repository-only revisions

A repository-only change is identified by its pull request and full Git commit
SHA. It does not become part of an existing supported container release merely
because it is merged to `main`.

GitHub Releases represent published container images; the project does not
create source-only releases or tags. Use the `Unreleased` changelog section for
notable changes intended for the next image release. At release time, move
those entries into a section named for the immutable release tag.

## Release requirements

Before an annotated release tag is pushed:

1. Verify that the tag matches the locked PostgreSQL version and UBI major and
   that metadata records the exact UBI reference and digest.
2. Convert `Unreleased` changelog entries into a dated section for the tag and
   create a new empty `Unreleased` section.
3. Complete all applicable build, runtime, upgrade, security, architecture, and
   release gates.
4. Merge the reviewed release change to protected `main` with required checks
   passing.
5. Create the annotated tag from that exact `main` commit.
6. Let the tag workflow build, scan, attest, sign, publish, and create the
   GitHub Release.
7. Verify manifest architectures, digest, signature, provenance, SBOM, labels,
   scan evidence, and release assets before announcing support.

The `sha-<short-commit>` tag supplements but never replaces the release tag and
digest.
