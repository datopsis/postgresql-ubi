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
appropriate. No response or remediation SLA is promised until the first
supported release defines one. Scanner matches require both PGDG and Red Hat
advisory context; version strings alone are not sufficient triage evidence.
