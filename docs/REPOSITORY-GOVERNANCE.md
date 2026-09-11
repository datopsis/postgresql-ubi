# Repository governance

## Protected development

The default branch is `main`. Image, workflow, security, and release-sensitive
changes use pull requests, review, and required checks. Workflows default to
read-only permissions and receive narrower write permissions only in the job
that requires them. Third-party Actions are pinned by full commit SHA.

Before the first release, configure rules that require the lint,
configuration-security, native AMD64/ARM64 image, aggregate image, and CodeQL
checks. Require conversation resolution and block force pushes and deletion.

## Release tags

Add a tag ruleset matching `docs/VERSION.md` only after the release workflow
and authorized actors are defined. It must prevent release-tag updates and
deletion. A GitHub Release represents a published container image, never a
source-only documentation revision.

## Security features

Keep dependency-graph alerts, Dependabot security updates, secret scanning,
push protection, CodeQL, OpenSSF Scorecard, and private vulnerability reporting
enabled where the organization plan supports them. Security reports use the
private advisory route, not public issues.

## Ownership

CODEOWNERS identifies review responsibility but does not replace branch rules.
Runtime, authentication, storage, entrypoint, package-source, workflow, and
release changes require explicit security and operational review.

The accountable roles, response expectations, and explicit single-maintainer
risk are recorded in [Maintenance and ownership](MAINTENANCE.md). The current
maintainer owns repository administration, but the first public release still
requires an independent security/release review. Do not bypass required checks
or weaken protections because an independent reviewer is unavailable; delay
the release instead.

## Public badge inventory

No badge is currently approved for publication in `README.md`. Badges summarize
external state and are not release evidence. The following inventory prevents
an aspirational badge from becoming an unsupported claim:

| Candidate | Decision | Evidence required before publication | Owner | Removal condition |
| --- | --- | --- | --- | --- |
| CI | Deferred until the artifact-lock gate closes | Public default-branch workflow showing all required checks | `@joey-huckabee` | Workflow disabled, required gate removed, or badge no longer points to `main` |
| OpenSSF Scorecard | Deferred until first-release repository settings are complete | Current public Scorecard run and documented interpretation | `@joey-huckabee` | Scan becomes stale, workflow disabled, or result cannot be inspected |
| Signed image | Deferred until a release exists | Public immutable digest plus successful Cosign verification instructions | `@joey-huckabee` | No currently supported signed digest or verification fails |
| SBOM | Deferred until a release exists | Digest-bound downloadable SPDX release asset or attestation | `@joey-huckabee` | Asset missing, expired, mismatched, or no longer covers a supported digest |
| FIPS, STIG, compliance, Red Hat certification, or support | Prohibited without separately approved evidence | Applicable validation/certification and exact supported boundary | `@joey-huckabee` | Any prerequisite expires, changes, or cannot be independently verified |

A badge change requires pull-request review of its destination, wording,
evidence, owner, and removal condition. A passing badge never broadens
[`docs/SUPPORT.md`](SUPPORT.md).
