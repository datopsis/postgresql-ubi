# PostgreSQL 18.7 refresh evidence (2026-11-18)

## Inputs and supplier review

The standard PGDG package seeds were selected from native primary repository
metadata, downloaded, and SHA-256 checked before dispatching the unchanged
native resolver workflow with `propose=false`:
[resolution run](https://github.com/datopsis/postgresql-ubi/actions/runs/44238733589).
The workflow verifies publisher signatures, resolves the UBI closure, acquires
source RPMs, and renders exact NEVRA/size/SHA-256 locks.

| Architecture | Previous PostgreSQL RPM version | Selected version |
| --- | --- | --- |
| AMD64 | 18.6-1PGDG.rhel9.8 | 18.7-1PGDG.rhel9.9 |
| ARM64 | 18.6-1PGDG.rhel9.8 | 18.7-2PGDG.rhel9.9 |

The ARM64 directory index showed `1PGDG.rhel9.8` while primary metadata already
advertised the downloadable `2PGDG.rhel9.9`. Primary metadata and exact bytes
were used. The x86_64 `10PGDG.rhel9.9` files are named
`babelfish_postgresql18*`, a distinct package family patched for Babelfish, not a newer release of
standard `postgresql18*`. The resolver consumes the three reviewed standard
seeds. Neither the old nor refreshed closure contains `postgresql18-contrib`.
No packages, signing keys, or sources are exempted from verification.

Sources: [AMD64 PGDG repository](https://download.postgresql.org/pub/repos/yum/18/redhat/rhel-9-x86_64/repodata/repomd.xml),
[ARM64 PGDG repository](https://download.postgresql.org/pub/repos/yum/18/redhat/rhel-9-aarch64/repodata/repomd.xml),
[PostgreSQL 18.7 release notes](https://www.postgresql.org/docs/release/18.7/).
The complete upstream CVE list is in `CHANGELOG.md`. Migration considerations
are recorded in `docs/STORAGE.md`.

## Scanner baseline

Counts below are High/Critical package findings classified by the unchanged
gate, per scanner (not deduplicated across scanners). Low/Medium findings remain
in retained raw reports. Deferred means the native query successfully proved
that the vendor-fixed version was unavailable in the pinned UBI repositories;
it does not mean fixed or exempted.

The [2026-11-17 main run](https://github.com/datopsis/postgresql-ubi/actions/runs/44131595403)
fails HTTP 404 during acquisition on both architectures. It cannot produce a
fresh 18.6 image or fresh scan; missing-report gate errors are failures, not
zero findings. The dated baseline is the
[last successful main CI run, 2026-11-15](https://github.com/datopsis/postgresql-ubi/actions/runs/43744164559)
at `d5b45103f8b3d5eb3827736b3ff367118da3b80d`. Its actual logs and retained
`gate.json`, Trivy, and Grype reports were read.

| Stage | Architecture | Scanner | Blocking | Deferred | Unfixed |
| --- | --- | --- | ---: | ---: | ---: |
| Before (2026-11-15) | amd64 | Trivy | 0 | 14 | 2 |
| Before (2026-11-15) | amd64 | Grype | 0 | 14 | 5 |
| Before (2026-11-15) | arm64 | Trivy | 0 | 14 | 2 |
| Before (2026-11-15) | arm64 | Grype | 0 | 14 | 5 |
