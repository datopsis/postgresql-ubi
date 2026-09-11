# Support contract

No supported container image has been released. Everything currently in this
repository is development material unless an immutable release and its evidence
are explicitly named by a published support statement.

## Classification terms

- **Supported** means an exact immutable image digest, architecture,
  configuration profile, host/runtime combination, and support period passed
  the documented release gates and is named by a published support statement.
- **Compatible** means limited tests demonstrated a behavior, but the project
  makes no production-support or security-maintenance commitment for that
  combination.
- **Preview/unqualified** means material is available for evaluation while
  required tests, operational guidance, or review remain incomplete.
- **Unsupported** means the project does not intend to qualify or maintain the
  behavior within the stated release boundary.

Absence from a matrix means unqualified, not implicitly compatible. A source
revision, locally built image, pull-request artifact, or successful CI run is
not a supported release.

## Current development matrix

| Area | Current classification | Evidence or limitation |
| --- | --- | --- |
| Published images | Unsupported | No release has been published. |
| Repository development image | Preview/unqualified | Runtime tests exist; artifact locks, release controls, and candidate evidence are incomplete. |
| Native Linux AMD64 and ARM64 | Preview/unqualified | Native CI builds, runtime tests, SBOMs, and scans exist; frozen-candidate and target-host evidence do not. |
| Rootless Podman | Preview/unqualified | It is the primary workflow, but exact RHEL/Podman/SELinux qualification remains open. |
| Docker | Compatible for CI behavior | Native Docker CI passes; this does not establish production equivalence with the planned Podman baseline. |
| OpenShift arbitrary UID | Preview/unqualified | The entrypoint is tested with an arbitrary UID in group 0; restricted-SCC deployment qualification remains open. |
| TLS | Compatible in native Docker CI | The mounted-certificate TLS 1.2/1.3 profile, trust/hostname/time failures, clear-text rejection, and rotation/rollback pass on AMD64 and ARM64; target Podman/platform qualification remains open. |
| Logical backup and restore | Compatible in native Docker CI | Custom-format dump, isolated restore, row/content validation, and an 18.4-to-18.6 update fixture pass on AMD64 and ARM64; scheduled target-platform restoration remains open. |
| Physical backup, WAL archive, and PITR products | Unsupported for v1 | Operators retain ownership; product-specific qualification is deferred. |
| PostgreSQL major-version upgrades | Unsupported for v1 | Other-major data directories are rejected; operators must plan pg_upgrade or logical dump/restore. |
| Replication, pooling, and high availability | Unsupported for v1 | These require separate topology, availability, and recovery qualification. |
| Additional extensions | Unsupported for v1 | Only the selected PGDG server/client package closure is in scope. |
| FIPS validation or approved mode | Unsupported | No PostgreSQL image cryptographic module or operational boundary has been validated. |
| STIG certification or system compliance | Unsupported | Planned SCAP evidence is limited to explicitly selected image-filesystem checks. |

## Approved first-release boundary

The first release will qualify:

- the current reviewed PostgreSQL 18 minor release on UBI 9 Minimal/Micro;
- native `linux/amd64` and `linux/arm64` images;
- an exact rootless Podman, RHEL 9, SELinux-enforcing, cgroup-v2 baseline;
- SCRAM-SHA-256 network authentication without a remote `trust` escape hatch;
- an operator-mounted TLS 1.2/1.3 server profile;
- one PostgreSQL instance with one operator-provisioned durable data volume;
- reviewed PostgreSQL 18 minor updates;
- logical `pg_dump`/`pg_restore` backup and restoration;
- verified connected and controlled-network acquisition/deployment procedures;
- digest-pinned deployment from immutable GHCR release tags; and
- tailored, explicitly bounded image-filesystem security evidence.

Docker remains a separately recorded compatibility claim. OpenShift remains
preview/unqualified unless an exact release passes the restricted-SCC procedure
before the release candidate is frozen. Client-certificate authentication and
role mapping are deferred for v1. Physical recovery guidance must identify
operator responsibilities but is not an image-managed service.

The image will not claim Red Hat support for PostgreSQL or this assembled
community image. Red Hat support, where a customer is eligible, is limited by
the Red Hat container support policy to covered Red Hat platform and UBI
components. Passing scans, using UBI, or producing SCAP results does not make
the image FIPS validated, STIG certified, or system-authorized.

## Ownership boundary

The image project owns verified inputs, image userspace, non-root defaults,
initialization and authentication behavior, declared writable paths and ports,
tests, release metadata, SBOM/provenance/signatures, and image vulnerability
response.

The host or orchestrator owns the kernel, container runtime, namespaces,
cgroups, seccomp, SELinux/AppArmor enforcement, network policy, firewall and
ingress, DNS, secrets, certificates and trust, persistent storage, backup
destinations, monitoring, log retention, time synchronization, node
vulnerability management, and decommissioning.

Database operators own roles and privileges, application schema, SQL and data
classification, configuration overrides, certificate lifecycle, capacity,
backup policy and successful restoration, minor-update approval, major-upgrade
planning, and incident integration. A persistent volume is not a backup.

## Support lifetime

The PostgreSQL 18 product line is intended to remain eligible for Datopsis
releases through PostgreSQL upstream's published final release date of
**2030-11-14**. Eligibility also requires usable, supported UBI 9 and PGDG
inputs. Each immutable Datopsis release is supported from its public support
announcement until the earliest of:

- 90 calendar days after a qualified successor is announced;
- withdrawal for a security, integrity, licensing, or distribution issue;
- the product-line end date; or
- loss of a required upstream input or support basis that cannot be replaced.

The current release receives normal maintenance. During the 90-day
supersession window, an older release receives security-only maintenance and
migration assistance; it receives no new compatibility work. End-of-support
dates are recorded in each release's support statement and qualification
record.

See [Maintenance and ownership](MAINTENANCE.md) for update cadence, security
response targets, withdrawal, and accountable roles.

## References

- [PostgreSQL versioning policy](https://www.postgresql.org/support/versioning/)
- [Red Hat container support policy](https://access.redhat.com/articles/2726611)
- [Red Hat Enterprise Linux life cycle](https://access.redhat.com/support/policy/updates/errata)
