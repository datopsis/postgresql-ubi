# Maintenance and ownership

This policy defines the first-release maintenance contract. It becomes an
external support commitment only for an immutable image whose release notes
and qualification record declare it supported.

## Accountable maintainers

The repository currently has one accountable maintainer. Role assignment does
not imply separation of duties that the project does not yet have.

| Responsibility | Accountable owner | Required record or action |
| --- | --- | --- |
| Image and PostgreSQL 18 maintenance | `@joey-huckabee` | Approve input changes, compatibility decisions, and supported-release updates. |
| PostgreSQL and PGDG security triage | `@joey-huckabee` | Review PostgreSQL security notices, release notes, PGDG packaging, source RPMs, and fixes. |
| UBI security triage | `@joey-huckabee` | Review Red Hat errata, base manifests, runtime RPM changes, and rebuild need. |
| Source and redistribution review | `@joey-huckabee` | Confirm each binary-to-source mapping, source availability, included licenses, UBI redistribution terms, and trademark boundaries on every lock change. |
| Artifact and signing-key policy | `@joey-huckabee` | Approve key additions, rotations, revocations, mirrors, and lock changes with fingerprint evidence. |
| Vulnerability reports and disclosure | `@joey-huckabee` | Monitor private advisories, acknowledge reports, coordinate suppliers, and publish advisories. |
| Release approval and GHCR administration | `@joey-huckabee` | Approve the candidate, protect immutable identity, publish or withdraw releases, and verify public artifacts. |
| Qualification and evidence retention | `@joey-huckabee` | Complete `docs/QUALIFICATION.md`, preserve durable evidence, and invalidate stale evidence. |

The single-maintainer model is an explicit availability, review-independence,
and account-compromise risk. The first public release still requires an actual
independent security/release review. Repository rules must not invent an
approval count that the available maintainer pool cannot satisfy, and required
checks, immutable tags, signed digests, or evidence review must not be bypassed
to compensate for staffing.

Deployment organizations must separately name owners for the database,
application, host/platform, storage, backups and restoration, PKI, network,
logging/SIEM, vulnerability acceptance, incident response, and authorization.

## Monitoring and update cadence

Maintainers review PostgreSQL, PGDG, and Red Hat security notices and available
updates at least weekly and whenever an upstream security release or credible
private report is received. Automated scheduled CI and dependency alerts are
inputs to review, not a substitute for advisory analysis.

| Input or event | Target action |
| --- | --- |
| PostgreSQL 18 minor release | Open a reviewed update candidate within 7 calendar days and target a qualified release within 14 calendar days. Always read every migration and security note. |
| Relevant Critical or known-exploited PostgreSQL, PGDG, or UBI issue | Begin assessment immediately; target mitigation, withdrawal, or a fixed qualified release within 72 hours when a safe fix exists. |
| Relevant High-severity fix | Target a fixed qualified release within 14 calendar days. |
| Other relevant security or correctness fix | Schedule according to exposure and vendor guidance, normally within 30 calendar days. |
| UBI base or runtime closure | Review at least weekly, re-qualify current inputs at least monthly while releases are supported, and rebuild whenever the reviewed closure changes. |
| PGDG/Red Hat signing key or repository policy | Review before accepting any changed key, fingerprint, source, redirect, or mirror. A failed verification blocks acquisition. |
| CI Actions, scanners, vulnerability databases, and assurance tools | Review alerts continuously and perform a pinned-version review at least monthly. |
| Support and security policy | Review at every release and at least quarterly. |

The weekly update dashboard compares the maintained PostgreSQL line with the
authoritative upstream versions feed. The scheduled lock resolver exercises
both architectures against current PGDG/UBI metadata and signing material;
Dependabot and Renovate propose pinned Actions, Python tools, UBI images,
scanners, Cosign, and assurance-tool changes. A bot proposal or green scheduled
run is only an alert: signing-key changes require fingerprint review, lock
changes require source/binary review, and scanner database changes invalidate
the affected evidence. See [the release supply chain](RELEASE.md).

Targets start when the project receives a credible report or an authoritative
notice is public, whichever occurs first. Severity is not accepted from a
scanner string alone: assessment includes vendor status, affected source and
binary packages, architecture, reachability, deployment exposure, data impact,
exploit maturity, and compensating controls.

If no safe supplier fix exists, the same target requires a published or private
risk decision, mitigation or withdrawal decision, accountable owner, and next
review date. It does not require an unsafe source fork or a misleading empty
scan. A release is delayed when required qualification cannot finish safely.

## Vulnerability response targets

- Acknowledge a private report within 2 business days.
- Produce an initial scope and severity assessment within 5 calendar days.
- For a relevant Critical or known-exploited issue, target containment or
  operator mitigation within 72 hours and a qualified fixed release within
  7 calendar days when a safe upstream fix is available.
- For a relevant High issue, target a qualified fixed release within
  14 calendar days when a safe upstream fix is available.
- For other relevant issues, target resolution in the next qualified release
  and no later than 30 calendar days unless a documented exception applies.

These are operational targets, not guaranteed resolution times. Coordinated
disclosure, incomplete reports, unavailable supplier fixes, or failed safety
qualification can change publication timing, but must not erase the record or
silently extend an exception.

Every accepted finding or suppression records the exact digest and
architecture, advisory, component, vendor status, rationale, exposure,
compensating control, accountable owner, approval, expiry, and rescan trigger.
Blanket and permanent ignores are prohibited.

## Supersession, withdrawal, and end of support

A qualified successor supersedes an older release when its digest, evidence,
support statement, migration notes, and rollback limits are public. The older
release then enters the 90-day security-only window defined in
[the support contract](SUPPORT.md#support-lifetime).

An image may be withdrawn for a confirmed compromise, exploitable defect,
invalid provenance or signature, exposed secret, licensing/distribution issue,
or evidence failure that makes continued use unsafe. Withdrawal requires:

1. recording the immutable tag and digest without moving or reusing either;
2. marking the GitHub Release and support statement as withdrawn;
3. publishing a security advisory or operational notice at the appropriate
   disclosure time;
4. identifying affected architectures, exposure, mitigation, replacement, and
   backup/restore or rollback constraints;
5. deciding whether public registry distribution must be removed or
   quarantined, while preserving restricted forensic evidence; and
6. notifying known consumers through established release channels.

No unsupported or withdrawn digest is silently rebuilt under an existing tag.
Normal end of support is announced at least 90 days in advance when upstream
events permit. An urgent security or legal withdrawal can be immediate.

## Evidence retention

- Pull-request and integration evidence is retained for at least one year when
  GitHub and repository storage permit.
- Release-candidate and published-release evidence is retained for the full
  support period plus one year, with release-critical evidence copied out of
  short-lived workflow artifacts.
- Within 24 hours of publication, copy release assets, raw manifest, Sigstore
  bundles, checksums, release metadata, and the qualification ledger to the
  access-controlled immutable backup named in the qualification record. Test
  retrieval annually and before a provider change; an untested backup is not
  release evidence.
- Security advisory and incident evidence follows the deployment
  organization's legal, privacy, and records policy and must not be placed in a
  public repository merely to satisfy this project policy.
- Credentials, private keys, database contents, internal endpoints, and
  unredacted sensitive logs are never qualification evidence.

Changing an input, behavior, configuration profile, tool database, assessment
procedure, or platform named by a record invalidates the affected evidence as
defined in [the roadmap](ROADMAP.md#evidence-lifecycle).
