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

## Live evidence before the lock refresh

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

In the pre-refresh run, both native image jobs correctly fail on available
High fixes; both complete runtime suites pass. Lint, configuration security,
CodeQL, and both SCAP jobs pass. No stalled util-linux refresh PR existed to
close. The subsequent approved lock refresh below addresses these blockers
without changing the gate decisions.

Live deferral of these two CVEs cannot be demonstrated truthfully now that the
fixed packages are published. The unavailable branch is covered by deterministic
tests. The tracking script was also dry-run against both actual native gate
reports. Issue creation/comments are unit-tested but the main-only scheduled
job cannot write during a PR run; it activates after merge. Release workflow
wiring is validated statically; publication/signing were not executed. No
repository settings, secrets, or branch protection were changed.

## Approved lock refresh in the same PR

The coordinator subsequently requested an RPM lock refresh in PR #29 now that
the fixed packages are published. The repository's unmodified
[update-locks workflow, run 43367289517](https://github.com/datopsis/postgresql-ubi/actions/runs/43367289517)
ran with `propose=false` on the PR branch. Base resolution and both native RPM
resolvers passed; no second PR was created. The generated locks and base inputs
were copied from those artifacts and validated with `scripts/artifacts.py`.

The AMD64 lock still contains 162 binary packages and the ARM64 lock 163;
each has 112 source RPMs. There are 41 binary version updates on AMD64 and 42
on ARM64, including its existing additional libatomic dependency; no packages
were added or removed. PostgreSQL 18.6 RPMs, their hashes, and approved signing keys are
unchanged. The selected base stream remains UBI 9.8: its rolling UBI 9
repositories supply the new packages, including the 9.9 release package.

| Base index | Before SHA-256 | After SHA-256 |
|---|---|---|
| builder | `4b79c93106c14ad1c234907f83441ff0e4f8d24e78426a36e159098e9f7e6fa5` | `f26ef64172ea61f5ac5ba4be8c5c738bf8760b22b3e5148ce7b40f7308ab32db` |
| runtime | `6d9eff186ce3ccf399c1835265e7fd3f83bd112cc3422da2d39fd44e234aab59` | `d3499a0896e2d6a1642f922615831bc5c2fd513bbb34f3446cabba530d9d54a2` |

Both architectures share the following version changes (epochs unchanged),
with one additional ARM64-only dependency update noted below:

| Packages | Before | After |
|---|---|---|
| acl, libacl | 2.4.0-1.el9_8 | 2.4.0-2.el9 |
| audit-libs | 3.1.5-8.el9 | 3.1.5-9.el9 |
| coreutils, coreutils-common | 8.32-41.el9_8.1 | 8.32-43.el9 |
| crypto-policies | 20260224-1.gitea0f072.el9_8 | 20260714-1.git65b74f7.el9 |
| dbus, dbus-common | 1.12.20-8.el9 | 1.12.20-10.el9 |
| dbus-broker | 28-9.el9_8 | 28-10.el9_9 |
| expat | 2.5.0-6.el9_8.7 | 2.5.0-9.el9_9.4 |
| gawk | 5.1.0-6.el9_8.1 | 5.1.0-7.el9 |
| glibc, glibc-common, glibc-minimal-langpack | 2.34-284.el9_8.4 | 2.34-290.el9_9 |
| libatomic (ARM64 only) | 11.5.0-14.el9 | 11.5.0-17.el9_9 |
| libattr | 2.6.0-1.el9_8 | 2.6.0-2.el9 |
| libblkid, libfdisk, libmount, libsmartcols, libuuid, util-linux, util-linux-core | 2.37.4-25.el9 | 2.37.4-28.el9_9.1 |
| libgcc, libstdc++ | 11.5.0-14.el9 | 11.5.0-17.el9_9 |
| libseccomp | 2.5.2-2.el9 | 2.5.6-1.el9 |
| libselinux | 3.6-3.el9 | 3.6-4.el9 |
| libxml2 | 2.9.13-14.el9_8.5 | 2.9.13-18.el9_9.1 |
| openldap | 2.6.8-4.el9 | 2.6.13-1.el9 |
| openssl, openssl-libs | 3.5.8-2.el9_8 | 3.5.9-1.el9_9 |
| pam | 1.5.1-28.el9_8.1 | 1.5.1-29.el9 |
| perl-Net-SSLeay | 1.94-3.el9 | 1.94-4.el9 |
| perl-URI | 5.09-3.el9_8.1 | 5.09-4.el9_9 |
| redhat-release | 9.8-1.0.el9 | 9.9-1.0.el9 |
| shadow-utils | 4.9-16.el9 | 4.9-17.el9 |
| systemd, systemd-libs, systemd-pam, systemd-rpm-macros | 252-67.el9_8.6 | 252-79.el9_9 |
| tzdata | 2026f-1.el9_8 | 2026f-1.el9_9 |
| xz-libs | 5.2.5-8.el9_8.1 | 5.2.5-8.el9_9.1 |

| Architecture | New artifact lock SHA-256 |
|---|---|
| amd64 | `ba43f37fac37b24014487e501e2bb6c6ed7a3bf614df294953796a1267835857` |
| arm64 | `eadfe8dd2fc097da68d66de97052359ee05fc2ea84c65264d4e9cae0c3c4e61f` |

The gate implementation is unchanged by the refresh. The Containerfile diff
changes only the two pinned base defaults; hardening and provenance labels
remain intact. Native post-refresh CI and the complete scanner comparison are
reported in [PR #29](https://github.com/datopsis/postgresql-ubi/pull/29).
