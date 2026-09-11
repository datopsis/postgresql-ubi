# Runtime security contract

## Initialization and authentication

Initialization is an all-or-stop operation for an empty `PGDATA`. An atomic
lock prevents concurrent initialization. A signal removes transient password
and lock files; any partial data remains deliberately blocked as a non-empty
directory without `PG_VERSION` and requires operator investigation.

`POSTGRES_PASSWORD_FILE` is preferred and subject to regular-file, symlink,
ownership, mode, readability, non-empty, and no-line-break checks.
`POSTGRES_PASSWORD` remains a compatibility interface; the container runtime's
configuration metadata can retain it even after it is unset from the final
PostgreSQL process. Passwords are passed to `initdb` only through a protected
temporary file, never command arguments. Core dumps are disabled.

The generated HBA file is short enough to audit completely and is replaced on
every start:

```text
# Managed by postgresql-ubi; replaced on every start.
local all all trust
host all all 0.0.0.0/0 scram-sha-256
host all all ::/0 scram-sha-256
```

The TLS profile changes both `host` records to `hostssl`. Local trust is
limited to the container's `/tmp` Unix socket and is not a host/network escape
hatch. Network passwords and every newly stored role password use
SCRAM-SHA-256. The image exposes no `POSTGRES_HOST_AUTH_METHOD` option.

`POSTGRES_USER` names the initial superuser and defaults to `postgres`;
`POSTGRES_DB` optionally creates one database. Neither variable changes an
existing cluster. Use PostgreSQL role administration for rotation and
least-privilege application roles as shown in `DEPLOYMENT.md`.

## Configuration precedence

Precedence from lowest to highest is PostgreSQL compiled defaults, the mounted
`POSTGRESQL_CONFIG_FILE`, user command-line options, and image-enforced final
options. The final options protect HBA location, SCRAM password storage, TLS
mode/protocol, Unix socket, stderr logging, statement/value exclusion, and core
operational events. `postgresql.auto.conf` cannot supersede command-line
settings. The server itself rejects malformed or unknown configuration before
accepting connections.

Inspect `pg_settings.source`, `sourcefile`, `pending_restart`, and effective
values after every change. Reload only reloadable parameters; replace/restart
for postmaster parameters. Retain the prior config and image for rollback.

## Logging and probes

PostgreSQL writes to stderr for runtime collection. Statement, duration, and
bind-parameter logging are forced off to prevent broad SQL/value capture.
Connection, disconnection, authentication failure, checkpoint, recovery, and
shutdown events remain available. Identifiers and client addresses may still
be sensitive operational metadata and need access, retention, and redaction
controls.

The OCI healthcheck is bounded `pg_isready` on the local socket. It indicates
that the server is accepting connections but does not authenticate or prove an
application transaction. External monitoring must use TLS verification and a
dedicated low-privilege role. Liveness must tolerate startup/recovery and avoid
restarting a merely saturated database.

`pgaudit` and all other audit extensions are deferred. Adding one requires new
locked RPM/source provenance, configuration, performance, log-volume,
vulnerability, upgrade, privacy, and maintenance decisions.

## Deliberately unsupported interfaces

- `/docker-entrypoint-initdb.d` execution is not implemented. It creates
  ordering, secret, retry, partial-execution, and ownership semantics that are
  not safe to imply without a separate contract.
- Client-certificate authentication and certificate-to-role mapping are not in
  the HBA policy. Server TLS does not imply mTLS.
- Remote trust authentication, root execution, privilege transition, added
  capabilities, writable root filesystems, and automatic reinitialization are
  not supported escape hatches.

## Comparison with the Docker Official Image

| Area | `postgresql-ubi` v1 contract | Docker Official `postgres` image | Compatibility consequence |
| --- | --- | --- | --- |
| Base/runtime | UBI 9 Micro final image; no package manager | Debian and Alpine variants | Package paths and utilities differ. |
| User | Fixed `26:0`; arbitrary UID with GID `0` | `postgres` user; mostly arbitrary UID behavior | Do not assume identical UID or ownership. |
| Data mount | `/var/lib/pgsql`, with `PGDATA=/var/lib/pgsql/data` | PostgreSQL 18 uses `/var/lib/postgresql`, with versioned `PGDATA` | Volume paths are not interchangeable. |
| Required secret | Non-empty password or strict regular `_FILE`; no line breaks/symlinks | `POSTGRES_PASSWORD` and `_FILE` supported | This image intentionally rejects more file layouts/modes. |
| Host auth | Remote SCRAM only; TLS profile requires `hostssl`; no trust override | Configurable `POSTGRES_HOST_AUTH_METHOD`, including documented trust option | Trust-based examples are incompatible by design. |
| Checksums | Always enabled | Optional through initdb arguments | Existing data characteristics can differ. |
| Init arguments/scripts | Fixed initdb policy; init scripts unsupported | `POSTGRES_INITDB_ARGS`, WAL-dir option, ordered shell/SQL init scripts | Move schema setup to explicit migration tooling. |
| Configuration | One mounted file plus args, with enforced final security settings | Standard PostgreSQL config/argument mechanisms | Security-critical overrides may be superseded here. |
| TLS | Tested mounted TLS 1.2/1.3 server profile | PostgreSQL mechanisms available; image-specific profile is operator-defined | Do not transfer TLS assumptions without review. |
| Health | Bounded local `pg_isready` | Variant/tag behavior must be inspected | Add external transaction monitoring separately. |
| Packages | Exact PGDG 18 server/client closure | Distribution-specific package set | Extensions/tools and CVE mapping differ. |
| Release identity | Planned immutable Datopsis tags/digests only | Official tag family includes mutable aliases | Pin the correct repository digest. |

The official image documentation describes broader `_FILE`, init-script,
arbitrary-user, and version-specific data-path behavior at
[Docker Official Image documentation](https://github.com/docker-library/docs/blob/master/postgres/README.md).
This table is a compatibility analysis, not a security or quality comparison.
