# Security policy

## Supported versions

No supported image has been published. Repository revisions and development
images are available for evaluation but receive no security-support commitment.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Use the repository's
**Security** tab and select **Report a vulnerability**:

<https://github.com/datopsis/postgresql-ubi/security/advisories/new>

Include the image tag and digest when available, architecture, runtime and host
versions, PostgreSQL configuration, reproduction steps, and whether the issue
appears to originate in this packaging, PostgreSQL, PGDG, or UBI. Remove
credentials, private keys, internal hostnames, and database contents.

Upstream vulnerabilities should follow the applicable upstream process:

- PostgreSQL: <https://www.postgresql.org/support/security/>
- Red Hat: <https://access.redhat.com/security/team/contact>

## Handling and disclosure

Maintainers will validate scope and coordinate disclosure with suppliers when
appropriate. Before the first supported release, the response targets below
are process objectives rather than an external support commitment. For a
published supported image, they apply from the earlier of a credible private
report or authoritative public notice:

- acknowledge a private report within 2 business days;
- provide initial scope and severity assessment within 5 calendar days;
- target containment or operator mitigation for a relevant Critical or
  known-exploited issue within 72 hours, and a qualified fixed release within
  7 calendar days when a safe supplier fix exists;
- target a qualified fixed release for other relevant High issues within
  14 calendar days when a safe supplier fix exists; and
- target other relevant resolutions within 30 calendar days unless a reviewed,
  owned, expiring exception documents why that is unsafe or impossible.

Scanner matches require PostgreSQL/PGDG and Red Hat advisory context, affected
package and architecture, reachability, exposure, and deployment impact;
version strings alone are not sufficient triage evidence. An unavailable fix
does not erase a target: it requires a mitigation, withdrawal, or documented
risk decision with an owner and next review date.

The complete cadence, exception requirements, withdrawal procedure, owner, and
evidence-retention rules are in
[Maintenance and ownership](docs/MAINTENANCE.md). Never disclose credentials,
private keys, database contents, personal data, or internal environment details
in a public issue or public evidence record.
