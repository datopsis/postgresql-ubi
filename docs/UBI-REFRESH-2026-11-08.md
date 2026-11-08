# UBI and RPM refresh: 2026-11-08

Status: candidate; owner review pending. No human approval is recorded.

## Base manifest indexes

| Base (9.8) | Previous SHA-256 | New SHA-256 |
| --- | --- | --- |
| builder | `sha256:7fbeae18dc9476399f565e68255f602a3374ea8614ba3d14843565131a13ff93` | `sha256:4b79c93106c14ad1c234907f83441ff0e4f8d24e78426a36e159098e9f7e6fa5` |
| runtime | `sha256:f332c99eb8f798a8486821c91937f10ad64ee83d7e739303be2df051040918f6` | `sha256:6d9eff186ce3ccf399c1835265e7fd3f83bd112cc3422da2d39fd44e234aab59` |

Both indexes were fetched from `registry.access.redhat.com` at tag `9.8`.
The raw manifest bytes match the registry digest headers; both contain exactly
one Linux AMD64 and one Linux ARM64 descriptor. Containerfile defaults, input
selection, architecture locks, and built-image labels retain the exact pins.

## Native resolution

[Resolver run](https://github.com/datopsis/postgresql-ubi/actions/runs/42441391785)
passed on both native runners using `resolve-lock.sh` and `render-lock.py`.
No package hashes were edited by hand. PostgreSQL seeds and signing keys did
not change. All changed inputs require fresh candidate evidence and owner review.

| Architecture | Binary RPMs before → after | Source RPMs before → after | Locked binary bytes after |
| --- | --- | --- | --- |
| amd64 | 161 → 162 | 111 → 112 | 76,560,631 |
| arm64 | 162 → 163 | 111 → 112 | 74,886,405 |

`perl-Unicode-Normalize` is newly selected by dependency resolution on both
architectures; no packages were removed. ARM64 retains its sole architecture-only
package, `libatomic`. The privilege-bit and world-writable-file checks remain
mandatory in the build and CI.

| Package | Previous epoch:version-release | New epoch:version-release | Architectures |
| --- | --- | --- | --- |
| ca-certificates | `0:2025.2.80_v9.0.305-91.el9` | `0:2026.2.92_v9.0.319-90.3.el9_8` | amd64, arm64 |
| expat | `0:2.5.0-6.el9_8.3` | `0:2.5.0-6.el9_8.7` | amd64, arm64 |
| gawk | `0:5.1.0-6.el9` | `0:5.1.0-6.el9_8.1` | amd64, arm64 |
| glibc | `0:2.34-275.el9_8` | `0:2.34-284.el9_8.4` | amd64, arm64 |
| glibc-common | `0:2.34-275.el9_8` | `0:2.34-284.el9_8.4` | amd64, arm64 |
| glibc-minimal-langpack | `0:2.34-275.el9_8` | `0:2.34-284.el9_8.4` | amd64, arm64 |
| krb5-libs | `0:1.21.1-10.el9_8` | `0:1.21.1-10.el9_8.1` | amd64, arm64 |
| libevent | `0:2.1.12-8.el9_4` | `0:2.1.13-1.el9_8` | amd64, arm64 |
| libxml2 | `0:2.9.13-14.el9_8.4` | `0:2.9.13-14.el9_8.5` | amd64, arm64 |
| openssl | `1:3.5.5-6.el9_8` | `1:3.5.8-2.el9_8` | amd64, arm64 |
| openssl-libs | `1:3.5.5-6.el9_8` | `1:3.5.8-2.el9_8` | amd64, arm64 |
| pcre2 | `0:10.40-6.el9` | `0:10.40-7.el9_8` | amd64, arm64 |
| pcre2-syntax | `0:10.40-6.el9` | `0:10.40-7.el9_8` | amd64, arm64 |
| perl-AutoLoader | `0:5.74-481.1.el9_6` | `0:5.74-484.el9_8` | amd64, arm64 |
| perl-B | `0:1.80-481.1.el9_6` | `0:1.80-484.el9_8` | amd64, arm64 |
| perl-Class-Struct | `0:0.66-481.1.el9_6` | `0:0.66-484.el9_8` | amd64, arm64 |
| perl-Errno | `0:1.30-481.1.el9_6` | `0:1.30-484.el9_8` | amd64, arm64 |
| perl-Fcntl | `0:1.13-481.1.el9_6` | `0:1.13-484.el9_8` | amd64, arm64 |
| perl-File-Basename | `0:2.85-481.1.el9_6` | `0:2.85-484.el9_8` | amd64, arm64 |
| perl-File-stat | `0:1.09-481.1.el9_6` | `0:1.09-484.el9_8` | amd64, arm64 |
| perl-FileHandle | `0:2.03-481.1.el9_6` | `0:2.03-484.el9_8` | amd64, arm64 |
| perl-Getopt-Std | `0:1.12-481.1.el9_6` | `0:1.12-484.el9_8` | amd64, arm64 |
| perl-IO | `0:1.43-481.1.el9_6` | `0:1.43-484.el9_8` | amd64, arm64 |
| perl-IPC-Open3 | `0:1.21-481.1.el9_6` | `0:1.21-484.el9_8` | amd64, arm64 |
| perl-POSIX | `0:1.94-481.1.el9_6` | `0:1.94-484.el9_8` | amd64, arm64 |
| perl-SelectSaver | `0:1.02-481.1.el9_6` | `0:1.02-484.el9_8` | amd64, arm64 |
| perl-Symbol | `0:1.08-481.1.el9_6` | `0:1.08-484.el9_8` | amd64, arm64 |
| perl-URI | `0:5.09-3.el9` | `0:5.09-3.el9_8.1` | amd64, arm64 |
| perl-Unicode-Normalize | `(added)` | `0:1.27-461.el9` | amd64, arm64 |
| perl-base | `0:2.27-481.1.el9_6` | `0:2.27-484.el9_8` | amd64, arm64 |
| perl-if | `0:0.60.800-481.1.el9_6` | `0:0.60.800-484.el9_8` | amd64, arm64 |
| perl-interpreter | `4:5.32.1-481.1.el9_6` | `4:5.32.1-484.el9_8` | amd64, arm64 |
| perl-libs | `4:5.32.1-481.1.el9_6` | `4:5.32.1-484.el9_8` | amd64, arm64 |
| perl-mro | `0:1.23-481.1.el9_6` | `0:1.23-484.el9_8` | amd64, arm64 |
| perl-overload | `0:1.31-481.1.el9_6` | `0:1.31-484.el9_8` | amd64, arm64 |
| perl-overloading | `0:0.02-481.1.el9_6` | `0:0.02-484.el9_8` | amd64, arm64 |
| perl-subs | `0:1.03-481.1.el9_6` | `0:1.03-484.el9_8` | amd64, arm64 |
| perl-vars | `0:1.05-481.1.el9_6` | `0:1.05-484.el9_8` | amd64, arm64 |
| systemd | `0:252-67.el9_8.4` | `0:252-67.el9_8.6` | amd64, arm64 |
| systemd-libs | `0:252-67.el9_8.4` | `0:252-67.el9_8.6` | amd64, arm64 |
| systemd-pam | `0:252-67.el9_8.4` | `0:252-67.el9_8.6` | amd64, arm64 |
| systemd-rpm-macros | `0:252-67.el9_8.4` | `0:252-67.el9_8.6` | amd64, arm64 |
| tzdata | `0:2026c-1.el9_8` | `0:2026f-1.el9_8` | amd64, arm64 |
| xz-libs | `0:5.2.5-8.el9_0` | `0:5.2.5-8.el9_8.1` | amd64, arm64 |

## Why the weekly updater stayed green

The [2026-11-02 run](https://github.com/datopsis/postgresql-ubi/actions/runs/41499475215)
only generated and uploaded candidates. It used a hard-coded old minimal base,
never resolved either mutable UBI tag, and had no commit, push, or PR job.
Its retained AMD64 candidate already contained the fixed PCRE2, OpenSSL,
ca-certificates, expat, libevent and libxml2 RPMs, but still named the old base
indexes. Those candidate locks were never committed for ordinary CI to consume.
The new workflow resolves common multi-architecture base pins, regenerates both
native locks, and proposes changed content with an explicit CI dispatch.
Timestamp-only changes do not produce PRs. Proposal branches never force-push.

Repository PR automation is also blocked by organization policy. On 2026-11-08,
the repository Actions permissions API returned
`can_approve_pull_request_reviews: false`; enabling it returned HTTP 409:
“The organization does not allow GitHub Actions to create or approve pull requests”.
Organization policy access returned HTTP 403. No policy was changed.
An owner must enable the organization/repository permission or configure the
repository-scoped `LOCK_UPDATE_TOKEN` described in
[artifact acquisition](ARTIFACT-ACQUISITION.md). Until then automated PR creation
cannot succeed; the workflow will report failure rather than a false green.

## Vulnerability and verification evidence

The [failed main CI run](https://github.com/datopsis/postgresql-ubi/actions/runs/41489408220)
reported 21 fixed High findings and one fixed Critical finding per architecture:
ca-certificates, expat, libevent, libxml2, openssl/openssl-libs, and
pcre2/pcre2-syntax. Every affected package is refreshed above, including PCRE2
`10.40-7.el9_8` and OpenSSL `1:3.5.8-2.el9_8`.

Trivy and Grype thresholds and fix-status policies are unchanged. No scanner
ignore, exception approval, or human sign-off has been added. nginx is absent
from both RPM closures and both SBOMs.

[Native PR CI](https://github.com/datopsis/postgresql-ubi/actions/runs/42441672580)
passed both image jobs, including all runtime tests, Trivy and Grype. The full
Grype reports retain 19 High matches per architecture (five distinct CVEs), all
marked `not-fixed` by its Red Hat 9 data; no Critical matches remain:

| Advisory | Component | Fix status and exposure requiring owner review |
| --- | --- | --- |
| CVE-2026-115506 | expat | Upstream fix exists; no fixed RPM in current UBI resolution. Untrusted XML entity expansion can exhaust CPU. |
| CVE-2026-76641 | expat | Upstream patch exists; no fixed RPM in current UBI resolution. Requires Expat external-entity parser processing. |
| CVE-2026-53613 | util-linux source family | No fixed RPM in current UBI resolution. Privileged fstab user/users mount race; this image strips setuid/setgid and runs non-root with no capabilities in documented deployments. |
| CVE-2026-53615 | util-linux source family | Upstream fix exists; no fixed RPM in current UBI resolution. Requires probing a crafted partition image; ordinary PostgreSQL service use does not do this. |
| CVE-2026-2007 | PGDG PostgreSQL packages | Vendor/scanner mismatch: [PostgreSQL fixes this in 18.2](https://www.postgresql.org/support/security/CVE-2026-2007/), while the image runs 18.6 and has no contrib RPM. The raw Red Hat namespace match has no version bound. |

The Expat linkage inventory does not show libexpat in postgres/psql, but indirect
reachability is not ruled out. Upstream and Red Hat references and fuller notes
are recorded per architecture in `compliance/vulnerability-exceptions.json`,
under `pending_findings`, with empty `approval` and a 2026-11-15 review deadline.
The approved `exceptions` array remains empty. These are observations of exact
CI image digests, not approvals for those images or subsequent rebuilds. Red
Hat's security-data API returned HTTP 403 during cross-checking; UBI fix
availability above is supported by native resolution and scanner vendor data.

[Repeated native resolution](https://github.com/datopsis/postgresql-ubi/actions/runs/42441688764)
passed on both architectures and produced byte-identical locks, including the
original generation timestamps. The proposal job was intentionally skipped on
the development branch; local integration tests verify push, PR creation and CI
dispatch ordering against a temporary Git remote with a stubbed GitHub CLI.

Local Podman was installed and attempted both rootless and with sudo; both
failed with `cannot clone: Operation not permitted`. Native GitHub CI supplies
the image builds, runtime tests, SBOMs, Trivy, and Grype evidence.
Local Python checks use the pinned tool versions with wheels for Python 3.11
ARM64; the committed hash-locked CI requirements target Python 3.13 AMD64.
Those CI requirement locks remain unchanged.

Final-head CI results are recorded in [PR #25](https://github.com/datopsis/postgresql-ubi/pull/25).
