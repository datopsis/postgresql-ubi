# PostgreSQL on Red Hat UBI

`postgresql-ubi` is a planned security-oriented, rootless PostgreSQL container
built on Red Hat Universal Base Image. The initial product line targets
PostgreSQL 18 on UBI 9, beginning with PostgreSQL 18.6.

> [!IMPORTANT]
> The project is under initial development. No supported container image has
> been released yet.

## Version baseline

- Repository and image: `postgresql-ubi`
- Planned image location: `ghcr.io/datopsis/postgresql-ubi`
- Maintained PostgreSQL major line: `18`
- Initial PostgreSQL version: `18.6`
- Initial UBI major line: `9`

PostgreSQL 18 receives upstream fixes through November 2030. The project will
track current PostgreSQL 18 minor releases rather than remain on 18.6. A move
to another PostgreSQL major version is a deliberate compatibility and data
upgrade decision, not an automatic dependency update.

## Development image

The current development image provides:

- a digest-pinned UBI 9 Minimal builder and UBI 9 Micro runtime;
- exact PGDG PostgreSQL 18.6 RPM selection;
- a package-manager-free final image;
- fixed non-root (`26:0`) and OpenShift-style arbitrary-UID execution;
- mandatory initialization credentials and SCRAM-SHA-256 network
  authentication;
- a persistent data volume with read-only-root compatibility;
- dropped-capability and `no-new-privileges` operation; and
- stateful smoke tests for initialization, authentication, persistence,
  shutdown, arbitrary UIDs, and incompatible data directories.

Architecture-specific locks now cover the complete binary dependency closure,
publisher keys, source RPMs, and digest-pinned UBI inputs. Artifact acquisition
is separate from a network-disabled, pull-disabled container build; see the
[artifact acquisition contract](docs/ARTIFACT-ACQUISITION.md).

Detailed procedures for choosing, deploying, verifying, operating, updating,
recovering, and safely removing each intended profile are in the
[deployment and operations guide](docs/DEPLOYMENT.md). The
[runtime security contract](docs/RUNTIME-SECURITY.md) and
[storage, backup, and upgrade guide](docs/STORAGE.md) define the associated
security and data-lifecycle boundaries.

## Approved first-release boundary

The first release is scoped to native AMD64 and ARM64, an exact rootless
Podman/RHEL 9 baseline, SCRAM-SHA-256 authentication, an operator-mounted TLS
server profile, one durable PostgreSQL instance, logical backup/restore,
reviewed PostgreSQL 18 minor updates, and verified controlled-network
procedures. Docker evidence is compatibility-only. OpenShift remains preview
unless an exact restricted-SCC environment is qualified before release.

High availability, physical backup/PITR products, major-version upgrade
qualification, extra extensions, client-certificate role mapping, broad
Kubernetes support, and FIPS validation are outside the initial release unless
the roadmap explicitly records later qualification. See the complete
[support contract](docs/SUPPORT.md),
[maintenance and ownership policy](docs/MAINTENANCE.md), and
[qualification schema](docs/QUALIFICATION.md).

## Build and test

Build and run the restricted-runtime test suite with rootless Podman:

```console
CONTAINER_RUNTIME=podman IMAGE=localhost/postgresql-ubi:development \
  bash scripts/build-offline.sh
CONTAINER_RUNTIME=podman IMAGE=localhost/postgresql-ubi:development \
  bash tests/smoke.sh
```

The preparation command requires Python 3, GnuPG, and rootless Podman. It
downloads only the current native architecture's committed artifacts, verifies
their exact bytes and publisher identities, pre-pulls the locked bases, and
then assembles with networking and further image pulls disabled. Remove the
ignored `.artifact-bundle/` directory before intentionally reacquiring it.

Start the Compose development service by supplying its secret from the host
environment:

```console
export POSTGRES_PASSWORD='replace-with-a-development-secret'
podman compose up
```

The service listens only on `127.0.0.1:5432`. Remove the development volume
deliberately with `podman compose down --volumes` when its database is no
longer needed.

## Initialization interface

The first start of an empty `/var/lib/pgsql` volume requires exactly one of:

- `POSTGRES_PASSWORD`; or
- `POSTGRES_PASSWORD_FILE`, which is preferred for orchestrator-mounted
  secrets.

`POSTGRES_USER` defaults to `postgres`. `POSTGRES_DB` optionally creates a
database with that name and otherwise defaults to `POSTGRES_USER`. Credentials
are used only for initial database creation; an existing PostgreSQL 18 data
directory starts without them. A data directory from another PostgreSQL major
version is rejected with an actionable error.

Host network authentication is SCRAM-SHA-256. The development image does not
provide a `trust` escape hatch for remote clients.

## Images and releases

Container releases use immutable annotated tags in this form:

```text
v<postgresql-version>-ubi<ubi-major>-r<YYYYMMDD>.<daily-sequence>
```

For example, `v18.6-ubi9-r20260910.1` identifies PostgreSQL 18.6 on the UBI 9
product line and the first Datopsis container release created on 2026-09-10
UTC. The example is not a published release.

The repository does not initially publish mutable tags such as `latest`, `18`,
or `18.6`. Production deployments should pin an immutable OCI digest. See the
[complete versioning and release policy](docs/VERSION.md).

## Support status

No supported image has been released. The current implementation is for
development and evaluation; consult the [support matrix](docs/SUPPORT.md)
before relying on any platform or operational claim.

## References

- [PostgreSQL versioning policy](https://www.postgresql.org/support/versioning/)
- [PostgreSQL 18.6 release notes](https://www.postgresql.org/docs/release/18.6/)
- [Red Hat Application Streams life cycle](https://access.redhat.com/support/policy/updates/rhel-app-streams-life-cycle)
- [Red Hat Universal Base Images](https://developers.redhat.com/products/rhel/ubi)
