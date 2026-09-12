# Release supply chain

No supported image exists yet. This document defines the mechanism. Package 8
must rehearse it with a disposable candidate, verify GitHub settings, obtain
independent approval, and publish the first supported release.

## Trust boundary

The annotated tag, protected-`main` commit, architecture manifests, OCI index,
labels, locks, SBOMs, scans, Sigstore bundles, and GitHub Release must identify
one candidate. Consumers verify
`ghcr.io/datopsis/postgresql-ubi@sha256:<digest>`; tags are discovery aids. The
workflow creates only the full release tag and `sha-<12>` commit tag—never
`latest`, `18`, or `18.6`.

`scripts/release.py` rejects impossible or non-current UTC dates, a reused
daily sequence, lightweight or moved tags, a commit outside `origin/main`, a
missing/misdated changelog section, and disagreement among tag, Containerfile,
input lock, or architecture locks. An existing GitHub Release also blocks
reuse. Package 8 adds the tag ruleset after the creation procedure is proven.

## Required GitHub configuration

Configure a `release` environment with independent required reviewers, no
bypass, and deployment limited to release tags. Keep default workflow-token
permissions read-only, expose no long-lived secret, permit only the pinned
Actions used here, enable immutable releases, and link GHCR to this repository.
Package 8 records actual settings because YAML cannot enforce them.

## Pipeline and least privilege

The tag workflow is non-cancelling. Jobs have no permissions beyond these:

| Job | Permission | Purpose |
| --- | --- | --- |
| Validate | `contents: read` | Validate history, locks, tag, ancestry, sequence, and release reuse. |
| Build | `contents: read` | Build/test native AMD64 and ARM64 archives; cannot publish. |
| Approve/publish | `contents: read`, `packages: write`, `release` environment | Upload exact archives by digest and create two immutable tags. |
| Registry scan | `contents: read`, `packages: read`, `security-events: write` | Validate and scan the published digest. |
| Sign | `contents: read`, `packages: write`, `id-token: write` | Attach evidence and keyless signatures after scans pass. |
| GitHub Release | `contents: write` | Publish durable evidence after verification. |

Native `ubuntu-24.04` AMD64 and `ubuntu-24.04-arm` ARM64 runners acquire their
checksum/fingerprint-locked closures, build without network access, run the
restricted-runtime suite, and export OCI archives. Each exact archive is
scanned and transferred using immutable GitHub Artifacts v4. ORAS uploads its
content by digest without staging tags; Buildx creates only the release and
commit tags. No pull-request artifact, cache, user-controlled expression, or
mutable artifact name enters the release.

The published index must contain exactly one Linux AMD64 and one Linux ARM64
descriptor. Scanner error, missing output, wrong architecture, fixed
High/Critical finding, or absent evidence blocks. Full Trivy and Grype JSON
keeps Unknown/Low/Medium and unfixed findings for review; a passing gate is not
a claim that the image has no vulnerabilities.

## Evidence and verification

Release assets include architecture and manifest SPDX JSON, complete Trivy and
Grype JSON, SARIF, OCI manifests, image configurations, locks, build metadata,
a digest/architecture ledger, SHA-256 inventory, and Sigstore bundles.
Architecture digests receive SPDX and build-provenance predicates; the index
receives SPDX and release-evidence predicates. The index digest is signed
keylessly with GitHub Actions OIDC.

Use values from the GitHub Release and never substitute a mutable tag:

```console
IMAGE=ghcr.io/datopsis/postgresql-ubi
DIGEST=sha256:<64-lowercase-hex-characters>
TAG=v<postgresql>-ubi9-r<YYYYMMDD>.<sequence>
IDENTITY="https://github.com/datopsis/postgresql-ubi/.github/workflows/release.yml@refs/tags/${TAG}"

cosign verify \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --certificate-identity "${IDENTITY}" \
  --bundle image.sigstore.json "${IMAGE}@${DIGEST}"
cosign verify-attestation \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --certificate-identity "${IDENTITY}" --type spdxjson \
  --bundle manifest-sbom.sigstore.json "${IMAGE}@${DIGEST}"
sha256sum --check SHA256SUMS
```

Also compare both platform digests to `release-evidence.json`, inspect raw OCI
labels, and perform the PostgreSQL checks in `QUALIFICATION.md`. OIDC exists
only in the signing job and grants no repository/registry permission itself.

## Retention and backup

Transfer archives expire after 7 days and workflow evidence after 90 days.
They are not durable records. The GitHub Release is the public copy. Within 24
hours, the qualification owner copies all assets, release metadata, raw index,
bundles, and checksum inventory to an access-controlled, versioned, immutable
backup; records its location and restore test in `QUALIFICATION.md`; and tests
retrieval annually and before changing providers. Preserve it through support,
the 90-day supersession window, and one additional year. Sensitive incident
evidence follows the stricter legal/privacy policy and is not published.

## Failure and quarantine

A build or pre-publication scan failure publishes nothing. Untagged manifests
uploaded before failure remain unannounced and unsigned. A post-index failure
quarantines its release and commit tags: no GitHub Release, support statement,
signature, or announcement. Record tag, digest, run, cause, architectures, and
disposition. Delete a package version only after proving no released index
references it and preserving forensic evidence; deletion can break consumers.
Never move or reuse a Git tag, OCI tag, digest, or daily sequence. Fix the cause
in a new reviewed commit and release identifier. A partially attached
attestation is evidence of a failed candidate, not authority to deploy.

## UBI-only emergency rebuild

A relevant Critical or known-exploited UBI issue starts immediate assessment
and the 72-hour containment/mitigation target; it does not wait for PostgreSQL.
Keep reviewed PostgreSQL/PGDG inputs unchanged, resolve both current UBI
closures and base manifests, review Red Hat errata and source/binary deltas,
verify signing identities, regenerate locks, and run all Package 2–4 gates.
Explain every filesystem, package, SBOM, behavior, and finding delta. Use a new
date/sequence and normal qualification/approval. If no safe fix is available,
record mitigation or withdrawal, owner, affected digests, and next review.
Never silently rebuild an existing tag.

## Workflow security review

Package 4 confirms SHA-pinned Actions, read-only defaults, explicit job grants,
disabled checkout credentials, no release cache/fork trigger, non-cancelling
concurrency, fixed artifact names, and OIDC confined after scanning. The
release environment separates approval from building. Immutable artifact IDs
prevent overwrite and missing evidence is fatal. Package 8 must observe the
external rulesets, environment reviewers, Actions policy, GHCR access, OIDC
claims, and independent review. Runner/action compromise remains residual risk
managed through pins, native duplication, attestations, evidence review, and
withdrawal—not eliminated by YAML.
