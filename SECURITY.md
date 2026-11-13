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

## Installable-fix vulnerability gate

CI and releases block High/Critical findings when a vendor fix can be installed
from the UBI repositories used to resolve this image's locked RPM closure. For
each vendor-fixed UBI RPM finding, a native query uses the repository files and
DNF configuration copied from that architecture's digest-pinned builder image
before installing query tooling. It refreshes every enabled UBI repository,
uses the resolver's release version and architecture, excludes installed
builder packages, and compares available versions with the vendor fixed
version using RPM epoch/version/release ordering. Any available version at or
above a vendor fixed version blocks the gate.

Only a successful query proving that no such version is available defers a
finding. Deferred findings remain vulnerabilities: the job summary and retained
JSON include the scanner, finding, package, architecture, vendor fixed version,
query result, and decision. They are not exemptions or approvals. Findings
without a vendor fix remain reported as unfixed, separately from deferrals.
There are no CVE, package, or date exceptions in this rule.

Query errors, deadlines, missing repositories, invalid versions, missing or
malformed scanner reports, and ambiguous package identities fail closed.
Only RPMs matching a locked UBI origin can be deferred; fixable PGDG or other
supplier RPMs and non-RPM findings (including application dependencies) keep
the ordinary blocking behavior. High/Critical secret findings also block.
The availability check never changes the runtime, locks, or repository sources.

Daily native CI rechecks current scanner data and UBI publication. On scheduled
runs (and manual runs on main), one **UBI vulnerability fix availability** issue
records both architectures and comments when findings, vendor versions, gate
decisions, or query errors change. When UBI publishes a fix, the next successful
query blocks and the tracking job still runs after the failed image job to
notify issue subscribers. Missing architecture evidence is reported as a
failure, never as resolution. Pull requests cannot write this issue. The
scheduled workflow becomes active after the change reaches main; this PR does
not change repository settings, secrets, or branch protection.
