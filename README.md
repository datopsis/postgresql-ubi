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

The current builder still resolves the locked package version from public
repositories. Network-disabled assembly from a checked artifact lock remains a
first-release gate; see [the roadmap](docs/ROADMAP.md) and
[package-source decision](docs/PACKAGE-SOURCE.md).

## Build and test

Build and run the restricted-runtime test suite with rootless Podman:

```console
podman build --format docker --file Containerfile \
  --tag localhost/postgresql-ubi9:development .
CONTAINER_RUNTIME=podman IMAGE=localhost/postgresql-ubi9:development \
  bash tests/smoke.sh
```

Start the Compose development service by supplying its secret from the host
environment:

```console
export POSTGRES_PASSWORD='replace-with-a-development-secret'
podman compose up --build
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
