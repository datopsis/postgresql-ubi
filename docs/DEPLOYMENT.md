# Deployment and operations guide

This guide describes every currently intended first-release deployment use
case. No supported image has been released yet, so examples use a locally
built development image. When releases exist, replace `IMAGE` with an
immutable `ghcr.io/datopsis/postgresql-ubi@sha256:<digest>` reference; never
substitute a mutable tag.

## Choose a deployment profile

| Use case | Runtime identity | Storage | Transport | Procedure |
| --- | --- | --- | --- | --- |
| Rootless Podman baseline | `26:0` | Named volume | TLS | Sections 1-4 and 7 |
| OpenShift-style identity evaluation | Arbitrary UID, GID `0` | Named volume or prepared bind mount | TLS | Sections 1-3, 5, and 7 |
| Host-managed database path | `26:0` or arbitrary UID/GID `0` | SELinux-labeled bind mount | TLS | Sections 1-3, 6, and 7 |
| Docker compatibility | `26:0` | Named volume | TLS | Sections 1-4 and 7, using Docker syntax |
| Compose development | `26:0` | Compose named volume | Isolated clear text or mounted TLS | Section 8 |
| Controlled network | Either qualified identity | Pre-provisioned storage | TLS | Sections 1-7 and 13 |

The non-TLS profile permits SCRAM-authenticated but unencrypted TCP traffic.
Use it only when traffic is confined by a separately enforced local or private
network boundary. The TLS profile changes host rules to `hostssl`, so clear-text
TCP connections are rejected rather than opportunistically accepted.

## 1. Establish prerequisites and ownership

1. Select the exact image digest, CPU architecture, runtime, host, storage
   implementation, network boundary, and TLS profile. Record these values in
   the deployment change record.
2. Install rootless Podman on the qualified RHEL 9 baseline. Docker is a CI
   compatibility target until a release support statement says otherwise.
3. Keep SELinux enforcing on RHEL. Do not disable labels to work around a mount
   denial; prepare the label as described below.
4. Provision durable storage separately from the container lifecycle. The
   volume must support PostgreSQL durability, locking, permissions, atomic file
   operations, and sufficient space and inodes. A persistent volume is not a
   backup.
5. Assign separate accountable owners for the database, storage, backups,
   certificate lifecycle, network policy, logging/SIEM, and image updates.
6. Set a termination grace period of at least 30 seconds as an initial value.
   Measure real shutdown and recovery behavior under peak workload before
   selecting a production value.

Set the runtime and immutable image reference for the remaining commands:

```console
export RUNTIME=podman
export IMAGE=localhost/postgresql-ubi:development
```

For a published release, verify its digest, signature, attestation, SBOM, and
support statement before creating storage or credentials. Release verification
commands will be published with Package 4; development builds are not a
substitute for that gate.

## 2. Prepare the initialization credential

The preferred interface is a mounted file. Create it without a trailing line
break and make it readable only by its owner, or by group `0` when the runtime
uses an arbitrary UID:

```console
umask 077
printf '%s' 'replace-with-a-random-secret' > postgres-password
chmod 0400 postgres-password
```

The entrypoint accepts only modes `0400`, `0440`, `0600`, or `0640`, rejects
symbolic links, rejects line breaks and empty values, and requires ownership by
UID `0` or the runtime UID. Group-readable files must use GID `0`. A CSI secret
driver that exposes symlinks is not compatible with this interface; configure
the driver to present a regular file or copy the secret into a protected
ephemeral volume before startup.

`POSTGRES_PASSWORD` is supported for bootstrap compatibility, but container
inspect APIs can retain its original value even after the process removes it
from the PostgreSQL environment. Use the file interface for deployments. Do
not place the value in shell history, command arguments, Compose YAML, Git,
logs, tickets, or qualification evidence.

The bootstrap value is used only when `PGDATA` is empty. It does not rotate an
existing role password.

## 3. Create and verify the network boundary

1. Permit port 5432 only from intended application, administration, backup, and
   monitoring sources.
2. Do not publish `0.0.0.0:5432` on a workstation. Bind a specific protected
   address or use an orchestrator network policy.
3. For TLS, distribute the issuing CA to clients through the organization's
   trust process and require `sslmode=verify-full` with the expected DNS name.
4. For the isolated non-TLS profile, prove that traffic cannot leave or enter
   the protected boundary. SCRAM protects the password exchange but does not
   encrypt query results or other session traffic.

## 4. Deploy with a named volume and fixed UID

Create the volume independently so replacing the container cannot delete it:

```console
$RUNTIME volume create postgresql-data
```

Start the isolated non-TLS profile for evaluation:

```console
$RUNTIME run --detach --name postgresql \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=64m,mode=1777 \
  --mount type=volume,src=postgresql-data,dst=/var/lib/pgsql \
  --mount type=bind,src="$PWD/postgres-password",dst=/run/secrets/postgres-password,readonly \
  --env POSTGRES_PASSWORD_FILE=/run/secrets/postgres-password \
  --publish 127.0.0.1:5432:5432 \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --stop-signal SIGINT \
  "$IMAGE"
```

Podman may require `--security-opt no-new-privileges`; Docker accepts
`--security-opt no-new-privileges:true`. Verify initialization and the effective
security boundary:

```console
$RUNTIME logs postgresql
$RUNTIME exec postgresql pg_isready --host=/tmp --timeout=3
$RUNTIME exec --env PGPASSWORD='replace-with-a-random-secret' postgresql \
  psql --host=127.0.0.1 --username=postgres --dbname=postgres \
  --command='SELECT version(), current_user;'
$RUNTIME exec postgresql sh -c \
  'id; grep -E "^(NoNewPrivs|CapEff):" /proc/1/status; ulimit -c'
```

Expected results are UID `26`, GID `0`, `NoNewPrivs: 1`, an all-zero effective
capability mask, core limit `0`, PostgreSQL 18.6, and an authenticated query.
Inspect logs for errors and confirm that no credential value appears.

## 5. Deploy with an arbitrary UID

Use an allowed nonzero UID and supplemental/primary GID `0`. The named volume
inherits a group-writable setgid layout from the image:

```console
$RUNTIME volume create postgresql-arbitrary-data
$RUNTIME run --detach --name postgresql-arbitrary \
  --user 10001:0 \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=64m,mode=1777 \
  --mount type=volume,src=postgresql-arbitrary-data,dst=/var/lib/pgsql \
  --mount type=bind,src="$PWD/postgres-password",dst=/run/secrets/postgres-password,readonly \
  --env POSTGRES_PASSWORD_FILE=/run/secrets/postgres-password \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  "$IMAGE"
```

The entrypoint uses `nss_wrapper` only when the UID is absent from `/etc/passwd`.
It never changes privilege. Confirm `id -u` is `10001`, all PostgreSQL processes
use that UID, and the effective capability mask is zero. This is not an
OpenShift support claim; restricted-SCC qualification remains a separate gate.

## 6. Deploy with a bind mount

Stop before changing ownership. For fixed UID operation:

```console
sudo install -d -o 26 -g 0 -m 2770 /srv/postgresql-ubi
sudo semanage fcontext -a -t container_file_t '/srv/postgresql-ubi(/.*)?'
sudo restorecon -Rv /srv/postgresql-ubi
```

If local policy permits Podman-managed private relabeling, `-v
/srv/postgresql-ubi:/var/lib/pgsql:Z` is an alternative. Do not use recursive
`chown` against an existing database without a reviewed backup and rollback
plan. For arbitrary UID `10001:0`, use owner `10001`, group `0`, and mode
`2770`, accounting for the rootless user-namespace mapping (`podman unshare
chown` may be required).

NFS root-squash commonly prevents the runtime UID from establishing ownership
and can expose unsuitable locking or durability semantics. Have the storage
administrator pre-provision ownership and validate PostgreSQL behavior; do not
disable root-squash as a shortcut. For CSI/PVC storage, record the driver,
access mode, `fsGroup`/UID behavior, reclaim policy, snapshot semantics, and
tested failure behavior. Only one PostgreSQL server may mount a v1 data volume
for write access.

Replace the named-volume mount in Section 4 with:

```console
--mount type=bind,src=/srv/postgresql-ubi,dst=/var/lib/pgsql
```

If startup reports that `PGDATA` cannot be created or written, fix host/CSI
ownership, mapping, mount state, capacity, or SELinux policy. Never run the
database as root or grant broad capabilities to bypass the failure.

## 7. Enable the TLS 1.2/1.3 profile

Obtain a server key and certificate chain from the deployment PKI. The
certificate needs the client-visible DNS name in its SAN. Keep the unencrypted
private key outside the image and Git repository:

```console
chmod 0444 server-chain.crt
chmod 0440 server.key
sudo chown root:0 server-chain.crt server.key
```

Add these mounts and variables to the Section 4 or 5 command:

```console
--mount type=bind,src="$PWD/server-chain.crt",dst=/run/tls/server.crt,readonly \
--mount type=bind,src="$PWD/server.key",dst=/run/tls/server.key,readonly \
--env POSTGRESQL_TLS_CERT_FILE=/run/tls/server.crt \
--env POSTGRESQL_TLS_KEY_FILE=/run/tls/server.key
```

Both variables are mandatory together. The key must meet the same strict file
rules as the password. The profile pins TLS 1.2 through 1.3 and replaces all
network HBA records with `hostssl ... scram-sha-256`. It does not enable client
certificate authentication or certificate-to-role mapping.

Verify from a separate client boundary:

```console
psql 'host=db.example.test dbname=postgres user=postgres sslmode=verify-full sslrootcert=/path/to/ca.crt' \
  --command="SELECT ssl, version FROM pg_stat_ssl WHERE pid=pg_backend_pid();"
```

Also prove that `sslmode=disable`, an incorrect hostname, and an untrusted CA
fail. Monitor certificate expiration. PostgreSQL reloads certificate files on
SIGHUP; stage complete replacement files atomically, send SIGHUP, establish a
new verified connection, and confirm the served serial. If validation fails,
restore the previous protected key/chain, send SIGHUP again, and reverify. Do
not remove the old material until the new connection is confirmed.

PostgreSQL documents server key mode `0600`, or root ownership with group-read
mode `0640`; this image additionally accepts their read-only equivalents. See
[Secure TCP/IP connections](https://www.postgresql.org/docs/18/ssl-tcp.html)
and [libpq certificate verification](https://www.postgresql.org/docs/18/libpq-ssl.html).

## 8. Deploy with Compose

The repository `compose.yaml` is a local-development profile. Export the secret
without placing it in the YAML, then start and verify:

```console
export POSTGRES_PASSWORD='replace-with-a-development-secret'
podman compose up --detach
podman compose ps
podman compose exec postgresql pg_isready --host=/tmp --timeout=3
```

The service binds only `127.0.0.1`, uses a named volume, read-only root,
bounded `/tmp`, no capabilities, and no-new-privileges. For production, use a
deployment-specific secret provider and immutable image digest. Add the TLS
mounts and variables from Section 7 or keep the port inside a proven isolated
boundary.

Stop without deleting data:

```console
podman compose down
```

Delete the volume only after backup-retention and decommission approval:

```console
podman compose down --volumes
```

## 9. Supply reviewed PostgreSQL configuration

Create a regular, immutable file that is not group/other writable or marked
setuid/setgid/sticky. Mount it read-only and set:

```console
--mount type=bind,src="$PWD/postgresql.conf",dst=/run/postgresql/postgresql.conf,readonly \
--env POSTGRESQL_CONFIG_FILE=/run/postgresql/postgresql.conf
```

Validate in a disposable container against a copy of production-like data,
then start and inspect every effective value with `SHOW` or `pg_settings`.
Changes marked `pending_restart` require replacement/restart; reloadable values
can use `SELECT pg_reload_conf()`. Preserve the previous file and image digest
for rollback.

The entrypoint applies these non-overridable values after mounted and
command-line configuration: SCRAM password storage, managed HBA path, `/tmp`
socket path, TLS profile state and protocol range, stderr-only logging, no
logging collector, no statement/duration/parameter logging, and connection,
disconnection, checkpoint, recovery, and shutdown event visibility. Attempts
to override them earlier on the command line are superseded. The managed HBA
file is replaced on every start.

## 10. Create application roles and rotate credentials

`POSTGRES_USER` creates the initial superuser; `POSTGRES_DB` optionally creates
one database. These variables are bootstrap inputs, not ongoing account
management. Connect through a protected administrative path and create a
separate least-privilege login:

```sql
CREATE ROLE app LOGIN PASSWORD 'generated-secret'
  NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
GRANT CONNECT ON DATABASE appdb TO app;
GRANT USAGE ON SCHEMA app TO app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA app TO app;
ALTER DEFAULT PRIVILEGES IN SCHEMA app
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app;
```

Tailor privileges to the application; the example is a starting point, not a
universal grant set. Rotate with an interactive protected administrator session
(`\password app`) or a secret-safe automation channel. Verify the new secret,
revoke the old one, update consumers, and avoid SQL text or command lines that
would retain the value.

Init scripts under `/docker-entrypoint-initdb.d` are deliberately unsupported
for v1. Run reviewed schema migration tooling after readiness using a dedicated
role and transaction/retry policy.

## 11. Configure probes, resources, and logs

- The OCI healthcheck runs bounded `pg_isready` over the local socket. Treat it
  as startup/readiness evidence, not proof that application transactions work.
- Use a TCP/TLS authenticated `SELECT 1` from outside the container for external
  transaction monitoring with a dedicated low-privilege role.
- Do not use expensive SQL as a liveness probe; load-induced probe failures can
  cause destructive restart loops. A liveness policy should distinguish a hung
  process from saturation and allow recovery startup to finish.
- Start with `/tmp` at 64 MiB, `shm_size` at least 256 MiB, sufficient file
  descriptors/PIDs for configured connections and workers, and a measured
  memory limit above PostgreSQL shared memory plus per-session/workload demand.
  These are safe test starting points, not universal production sizing values.
- Alert on volume bytes and inodes before exhaustion, connection saturation,
  repeated authentication failures, checkpoints, recovery, OOM kills, and
  abnormal shutdown. Size termination grace from observed checkpoint/shutdown
  time and large-WAL crash recovery.

Logs stay on stdout/stderr. Collect them with runtime/orchestrator metadata and
access controls. The immutable profile disables statement, duration, and bind
parameter logging because SQL and values can contain credentials, personal
data, regulated data, or application secrets. Database/user/application/client
identifiers can also be sensitive; choose non-personal identifiers and apply
retention/redaction controls. Broad statement logging is not a substitute for
an audit design. PostgreSQL audit extensions are not included in v1.

## 12. Back up, restore, update, and recover

Follow [Storage, backup, and upgrade operations](STORAGE.md). At minimum:

1. define RPO/RTO, scope, owner, schedule, retention, immutability, encryption,
   access, and deletion policy;
2. run `pg_dump` or `pg_dumpall` through a TLS-verified connection into a
   separately protected destination;
3. record the image digest, PostgreSQL version, options, timestamps, and backup
   digest without recording contents or credentials;
4. restore into an isolated empty database on a schedule;
5. validate schema, role handling, row counts, and application-specific content
   digests, then record measured recovery time; and
6. retain the previous image digest and a verified pre-update backup. Do not
   assume that starting older binaries on newer database files is a safe
   rollback.

## 13. Controlled-network deployment

Use the verified bundle-transfer procedure in
[External artifact acquisition](ARTIFACT-ACQUISITION.md#controlled-network-transfer).
Transfer the immutable image by digest with its signature, attestations, SBOM,
scan results, lock, and verification instructions. Map the public digest to the
internal registry without rebuilding or changing bytes, configure internal CA
trust through the host/runtime trust mechanism, verify again inside the target
boundary, and refresh vulnerability databases through a separately controlled
process. Never embed repository credentials or private CAs in the image.

## 14. Failure diagnosis and data-preserving removal

- Missing/invalid credential: correct the protected secret only when the data
  directory is empty. Credentials are not required for an existing cluster.
- Non-empty directory without `PG_VERSION`: stop and preserve it. Investigate
  interrupted initialization or a wrong mount; never delete or reinitialize it
  automatically.
- Initialization lock: confirm no initializer is running. Preserve partial
  contents and obtain backup/storage-owner approval before removing a stale
  `<PGDATA>.postgresql-ubi.init.lock`.
- Wrong PostgreSQL major: do not edit `PG_VERSION`. Follow the major-upgrade
  decision in `STORAGE.md`.
- Read-only, permission, SELinux, NFS, CSI, disk-full, or inode-full failure:
  correct the underlying storage condition while stopped. Do not run as root.
- Crash/OOM/forced termination: preserve the volume, allow WAL recovery, review
  logs, verify application data, and take a fresh backup after recovery.

Remove only the container while preserving data:

```console
$RUNTIME stop --time 30 postgresql
$RUNTIME inspect postgresql --format '{{.State.ExitCode}}'
$RUNTIME rm postgresql
$RUNTIME volume inspect postgresql-data
```

Destructive decommissioning requires a verified retained backup or approved
retention expiry, consumer shutdown, credential/certificate revocation, legal
and records approval, and storage-specific secure deletion. Only then remove
the named volume explicitly. Container removal alone is not evidence that
database blocks, backups, WAL, snapshots, logs, or secrets were destroyed.
