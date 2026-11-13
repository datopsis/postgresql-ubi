# Native UBI fix-availability gate evaluation

## Decision and assumptions

The owner defines a fixable UBI RPM finding as one whose fixed or newer version
is available from the repositories used by this image. The change is a general
availability rule, not a CVE exception. The November 11 publication gap must not
be assumed to persist: live repository results decide each run.

[Trivy uses vendor advisories for OS packages](https://trivy.dev/docs/dev/guide/scanner/vulnerability/),
and [Grype's fixed-state filter](https://oss.anchore.com/docs/guides/vulnerability/filter-results/)
does not establish availability in a particular repository. This gate retains
those reports and makes the additional repository query explicitly.
[DNF available queries](https://dnf.readthedocs.io/en/latest/api_queries.html)
exclude installed packages; the query loads no system RPM database. Native
`rpm.labelCompare` handles epoch/version/release, including later release
suffixes, rather than lexical or application-version ordering.

The repository identity is the configuration copied from the digest-pinned
builder before installing DNF, with the resolver's releasever=9 and the native
architecture. All three configured UBI binary repositories must load; metadata
errors cannot become an empty successful query. Native and noarch candidates
are eligible. Locked non-UBI suppliers do not become eligible for deferral merely
because their packages are absent from UBI.

## Live evidence

[Native CI run 43366030749](https://github.com/datopsis/postgresql-ubi/actions/runs/43366030749)
built and tested both architectures, retained both complete scanner JSON reports,
and queried the pinned repositories on native runners. The query completed
without errors on both architectures. The original pinned `ubi.repo` SHA-256
was `f59e1e4c2f20048ef3204f5c81d23b04aac53a7d789b1f4d055a937867109f13`
on both. Base pins, RPM locks, and the runtime were unchanged.

The evidence disproves the initial expectation that the util-linux findings
would still be deferred: UBI now publishes `2.37.4-28.el9_9.1` on both
architectures. This satisfies both vendor fixes: `2.37.4-28.el9_9` for
CVE-2026-53613 and `2.37.4-28.el9_9.1` for CVE-2026-53615. All seven family
packages therefore block in both scanners. These identifiers are observations
only; the gate contains no matching exceptions.

Counts below are package/advisory matches, not unique CVEs. Each native run
exercised 33 vendor-fixed matches across the two scanners (66 total), alongside
35 unfixed matches. Cached name/architecture lookups avoid duplicate queries
without changing per-finding version comparisons.

| Scanner | Architecture | Vendor-fixed High before gate | Blocked | Deferred | Unfixed High retained | Critical |
|---|---|---:|---:|---:|---:|---:|
| Trivy | amd64 | 19 | 19 | 0 | 16 | 0 |
| Trivy | arm64 | 19 | 19 | 0 | 16 | 0 |
| Grype | amd64 | 14 | 14 | 0 | 19 | 0 |
| Grype | arm64 | 14 | 14 | 0 | 19 | 0 |

The other Trivy blockers also have available UBI fixes:

| Package | Findings | Available version |
|---|---|---|
| expat | CVE-2026-66046, CVE-2026-77214, CVE-2026-93990 | 2.5.0-9.el9_9.4 |
| libxml2 | CVE-2026-74860, CVE-2026-86140 | 2.9.13-18.el9_9.1 |

The native query plus bootstrap and comparison tests took about eight seconds on
each architecture in this run; full image jobs also include runtime tests and
scanner database acquisition. All repository queries used the public
`https://cdn-ubi.redhat.com/content/public/ubi/dist/ubi9/9/` tree, with
`x86_64` or `aarch64` and the BaseOS, AppStream, and CodeReady Builder components.
The gate artifacts retain the exact builder reference, lock hash, repository
URLs, query results, vendor versions, and reasons.

## Validation and limits

Local unit tests and native CI exercise available-to-block,
unavailable-to-report, query errors/timeouts, malformed versions/reports,
missing repositories, non-RPM findings, unrecognized origins, notification
state changes, and unchanged-state deduplication. Native UBI tests compare
13 epoch/version/release cases with librpm and exercise the available query
adapter. YAML, actionlint, shellcheck, and LF checks pass.

Both native image jobs correctly fail on available High fixes; both complete
runtime suites pass. Lint, configuration security, CodeQL, and both SCAP jobs
pass. This policy PR does not refresh inputs to conceal that result. No stalled
util-linux refresh PR existed to close.

Live deferral of these two CVEs cannot be demonstrated truthfully now that the
fixed packages are published. The unavailable branch is covered by deterministic
tests. The tracking script was also dry-run against both actual native gate
reports. Issue creation/comments are unit-tested but the main-only scheduled
job cannot write during a PR run; it activates after merge. Release workflow
wiring is validated statically; publication/signing were not executed. No
repository settings, secrets, or branch protection were changed.
