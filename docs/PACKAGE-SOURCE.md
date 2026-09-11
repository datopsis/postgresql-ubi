# PostgreSQL package-source decision

## Decision

Use the PostgreSQL Global Development Group's official PGDG RPM repository for
PostgreSQL 18 while retaining digest-pinned Red Hat UBI 9 Minimal and Micro base
images. Pin the exact RPM epoch, version, release, architecture, dependency
closure, repository package, checksums, and signing identity.

An inspection on 2026-09-11 found that the public UBI 9.8 repositories expose
PostgreSQL 13.23 but not the PostgreSQL 18 stream. The PGDG RHEL 9 repository
exposes these PostgreSQL 18.6 packages for x86_64:

```text
postgresql18-0:18.6-1PGDG.rhel9.8.x86_64
postgresql18-libs-0:18.6-1PGDG.rhel9.8.x86_64
postgresql18-server-0:18.6-1PGDG.rhel9.8.x86_64
```

The observed PGDG repository key fingerprint was:

```text
D4BF 08AE 67A0 B4C7 A1DB CCD2 40BC A2B4 08B4 0D20
```

These are observed development inputs, not a permanent lock or release claim.
The first release requires equivalent availability and native tests on AMD64
and ARM64 plus an external artifact lock and network-disabled assembly.

The development build enables only the PGDG 18 application repository from the
PGDG set. Older major-version and PGDG common repositories are disabled so they
cannot influence the dependency closure; RPM and repository-metadata signature
checks remain enabled for the selected source.

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
