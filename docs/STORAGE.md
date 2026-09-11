# Storage, backup, recovery, and upgrade operations

## Durable-state contract

The only declared persistent mount is `/var/lib/pgsql`; `PGDATA` is
`/var/lib/pgsql/data`. One v1 PostgreSQL server owns one writable volume.
PostgreSQL clusters are initialized with data page checksums. The image writes
only to the persistent mount and bounded `/tmp` when its root filesystem is
read-only.

The operator owns capacity, inode availability, latency, durability, filesystem
semantics, encryption at rest, snapshots, replication below the filesystem,
and recovery from node/storage loss. Monitor bytes and inodes independently.
Do not use NFS or a CSI driver until its locking, fsync, ownership, failure,
snapshot, and recovery semantics have been tested with the exact platform.

Fast shutdown uses SIGINT and aborts active transactions before checkpointing.
Forced termination can require WAL replay; PostgreSQL warns that SIGKILL should
be reserved for emergencies. See
[Shutting down the server](https://www.postgresql.org/docs/18/server-shutdown.html).

## Logical backup and restoration

Logical backup/restore is the v1 qualified recovery interface. Decide whether
the unit is a database (`pg_dump`) or the cluster's globals plus databases
(`pg_dumpall` plus per-database dumps). A per-database dump does not include all
cluster roles and tablespaces.

Example custom-format backup through a verified TLS connection:

```console
umask 077
export PGSSLMODE=verify-full
export PGSSLROOTCERT=/run/secrets/postgresql-ca.crt
pg_dump --host=db.example.test --username=backup --dbname=appdb \
  --format=custom --file=appdb.dump
sha256sum appdb.dump > appdb.dump.sha256
```

Supply the password through a protected password file or secret broker, not a
command argument. Encrypt the backup before it leaves the protected execution
boundary, using an organizationally approved mechanism and separately managed
key. Restrict read/delete access, make retained copies immutable where policy
requires, replicate to the approved failure domain, and test key recovery.

Restore only into an isolated empty target first:

```console
sha256sum --check appdb.dump.sha256
createdb --host=restore.example.test --username=restore_owner appdb_restore
pg_restore --host=restore.example.test --username=restore_owner \
  --dbname=appdb_restore --exit-on-error --no-owner appdb.dump
```

Review whether ownership must be preserved instead of using `--no-owner`.
Validate schema/migration versions, row counts, constraints, application-level
content digests, privileges, and an application transaction. Record start/end
UTC time and measured recovery time. Schedule isolated restoration at least
quarterly and after material schema, backup-tool, encryption, or version
changes. The database/backup owner defines the tighter schedule required by
RPO/RTO or regulation.

PostgreSQL describes logical, filesystem, and continuous-archive approaches in
[Backup and Restore](https://www.postgresql.org/docs/18/backup.html).

## Physical backup, WAL, PITR, and snapshots

These are operator-owned and not qualified v1 features:

- `pg_basebackup` requires a narrowly scoped replication role, HBA allowance,
  `max_wal_senders`, complete protected output, and a restoration exercise.
- Continuous archiving needs an uninterrupted WAL sequence beginning before
  the base backup, durable archive commands, monitoring, retention, timelines,
  recovery targets, and tested restoration. Logical dumps cannot supply WAL
  replay.
- Storage snapshots require a database-consistent procedure, crash-consistent
  semantics or coordinated backup API, all volumes/WAL, encryption, ordering,
  retention, and restoration testing. Copying a live data directory is not
  automatically a valid backup.

The presence of `pg_basebackup` does not establish an operational product. See
[pg_basebackup](https://www.postgresql.org/docs/18/app-pgbasebackup.html) and
[continuous archiving/PITR](https://www.postgresql.org/docs/18/continuous-archiving.html).

## PostgreSQL 18 minor update

Minor releases retain the major data format, but every update still requires
review and qualification:

1. read all PostgreSQL release notes, PGDG packaging changes, UBI errata, and
   known application/extension issues;
2. review both architecture lock diffs, sources, signing identities, complete
   RPM closure, image filesystem, SBOM, and vulnerability results;
3. retain the old image digest and create/verify a pre-update logical backup;
4. clone representative protected data into an isolated environment;
5. start the new digest on the preserved PostgreSQL 18 data, allow recovery,
   and test schema migrations, application transactions, query plans where
   relevant, backup, and isolated restore;
6. stop the old deployment cleanly, snapshot/backup according to policy, then
   replace only the container while preserving its volume;
7. verify version, checksum state, data counts/digests, roles, TLS, logs,
   readiness, application transactions, and backup after deployment; and
8. record elapsed shutdown/start/recovery time and the exact old/new digests.

Rollback means restoring the previous backup/snapshot with the previous image,
or applying a reviewed forward fix. Do not assume an older PostgreSQL binary
can safely open files after a newer minor has started them. The initial 18.6
image has no earlier supported Datopsis digest. Native CI therefore uses the
immutable Docker Official PostgreSQL 18.4 architecture digests as
preserved-data compatibility fixtures, verifies their platform and version,
takes a pre-update logical backup, adapts only the documented mount layout,
starts 18.6, validates application data, and takes another dump. This is
development update evidence, not support for the official image or a
substitute for repeating the procedure between Datopsis release digests.

## Major upgrade decision

The entrypoint rejects a data directory whose `PG_VERSION` is not `18`; never
edit that file.

Choose logical dump/restore when downtime and data volume permit it, when a
clean logical transformation is desired, or when extension/platform binary
compatibility is uncertain. Choose `pg_upgrade` only after both old and new
binaries, extensions, locales, collations, storage layout, link/copy mode,
rollback point, disk capacity, and the exact procedure have been qualified.
Either path requires verified backup, rehearsal, application validation,
cutover/rollback criteria, and retained evidence. No major upgrade is qualified
for v1.
