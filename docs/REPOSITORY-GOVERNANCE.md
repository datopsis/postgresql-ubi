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
