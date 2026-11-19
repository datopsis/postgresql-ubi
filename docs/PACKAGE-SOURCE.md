# PostgreSQL package-source decision

## Decision

Use the PostgreSQL Global Development Group's official PGDG RPM repository for
PostgreSQL 18 while retaining digest-pinned Red Hat UBI 9 Minimal and Micro base
images. Pin the exact RPM epoch, version, release, architecture, complete
dependency closure, checksums, source RPMs, and signing identity.

An inspection on 2026-09-11 found that the public UBI 9.8 repositories expose
PostgreSQL 13.23 but not the PostgreSQL 18 stream. The PGDG RHEL 9 repository
was selected for the initial build. The current PostgreSQL 18.7 inputs use
`18.7-1PGDG.rhel9.9` on x86_64 and `18.7-2PGDG.rhel9.9` on aarch64, selected
from each architecture's primary repository metadata on 2026-11-18. All three
seed packages (`postgresql18`, `postgresql18-libs`, `postgresql18-server`) use
that architecture's release. The directory listing can lag primary metadata;
the older aarch64 `1PGDG.rhel9.8` listing is not the newest candidate.

The visible x86_64 `18.7-10PGDG.rhel9.9` build belongs to the separate
`babelfish_postgresql18` package family. It is not a higher release of the
standard `postgresql18` package and is not selected for this image. The normal
resolver installs the reviewed, checksum-pinned standard PostgreSQL seeds;
it does not choose between unrelated package names. `postgresql18-contrib`
is not in this image's existing closure and is not added by this refresh.

Lock inputs may override `postgresql_rpm_version` per architecture when PGDG
publishes different native build releases. Each rendered lock still requires
an exact version/release for every PostgreSQL RPM. Offline assembly takes the
RPM-version image label from that native lock, and release validation checks
the corresponding architecture's selection.

The observed PGDG repository key fingerprints were:

```text
x86_64: D4BF 08AE 67A0 B4C7 A1DB CCD2 40BC A2B4 08B4 0D20
aarch64: B031 F89F C983 E982 6290 6B6E 177B 343B B973 8825
```

The reviewed locks in `artifacts/locks/` record these identities plus every UBI
runtime dependency and corresponding source RPM. Only the manual
`update-locks.yml` workflow resolves repository metadata. Ordinary builds
download exact locked files outside the container build, verify hashes,
signatures, fingerprints, metadata, architecture, and source correspondence,
then install the complete local transaction without DNF or repository access.

## Supplier boundary

PostgreSQL and PGDG are the application publisher and packager; Red Hat remains
the base-image and UBI dependency supplier. This combination is not a Red Hat
PostgreSQL support claim. Security review must consider advisories and package
metadata from both suppliers.

## References

- <https://www.postgresql.org/download/linux/redhat/>
- <https://download.postgresql.org/pub/repos/yum/>
- <https://www.postgresql.org/support/versioning/>
- <https://developers.redhat.com/products/rhel/ubi>
