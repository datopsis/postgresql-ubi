# Security architecture and trust boundaries

These diagrams define ownership and evidence boundaries. Arrows crossing a
boundary require validation; a green build does not make an external service
trusted.

## Component architecture

```mermaid
flowchart LR
  Client[Application client] -->|PostgreSQL protocol| Net[Deployment network policy]
  Net --> DB[postgresql-ubi container]
  Secret[Secret service] -->|read-only secret file| DB
  Config[ConfigMap or protected files] -->|read-only configuration| DB
  DB --> Data[(Durable PGDATA)]
  DB --> Temp[(bounded tmpfs /dev/shm and /tmp)]
  DB -->|stderr| Logs[Runtime logs / SIEM]
  Host[Host kernel + OCI runtime] --- DB
```

The image owns packaged files, entrypoint validation, and safe defaults. The
deployment owns configuration, identities, listeners, secrets, data, and
resources. The host/platform owns kernel isolation, SELinux, seccomp, cgroups,
network enforcement, and log transport.

## Build and assurance pipeline

```mermaid
flowchart LR
  PGDG[PGDG RPMs + SRPMs + keys] --> Verify[Hash/signature/source verification]
  UBI[Digest-pinned UBI stages] --> Verify
  PR[Reviewed commit] --> CI[Protected GitHub Actions]
  Verify --> Offline[Networkless final build]
  CI --> Offline
  Offline --> Test[Native amd64 + arm64 tests]
  Test --> Scan[Trivy + Syft/Grype + SCAP discovery]
  Scan --> Candidate[Candidate digest + evidence]
  Candidate --> Sign[Release attestation and signature]
  Sign --> GHCR[Immutable GHCR publication]
```

Untrusted pull-request code never receives release credentials. Locks,
publisher keys, action commits, scanner versions, evidence, tags, and registry
digests are substitution targets and require independent verification.

## Runtime data flow

```mermaid
sequenceDiagram
  participant S as Secret service
  participant E as Entrypoint
  participant D as PGDATA volume
  participant P as PostgreSQL
  participant C as Client
  participant L as Log collector
  S->>E: bootstrap password file
  E->>D: initialize only if empty
  E->>P: exec postgres as nonroot
  C->>P: authenticated SQL over selected TLS policy
  P->>D: WAL and data writes
  P->>L: operational/audit events via stderr
```

Initialization consumes the secret without copying it into the image or
command line. Existing data bypasses bootstrap; operators own continuing role
and secret lifecycle.

## Credential and TLS trust

```mermaid
flowchart TD
  OrgPKI[Organization PKI] --> Cert[Server certificate]
  OrgPKI --> ClientCA[Client trust store]
  SecretSvc[Secret service] --> Bootstrap[Bootstrap secret file]
  Bootstrap --> SCRAM[SCRAM verifier in PGDATA]
  Cert --> Server[PostgreSQL TLS endpoint]
  ClientCA --> Client[Client sslmode=verify-full]
  Client -->|hostname + chain + TLS| Server
  DNS[Trusted DNS] --> Client
  Time[Trusted time] --> Client
  Time --> Server
```

PKI, DNS, clock, client verification, rotation, and revocation are outside the
image. SCRAM does not replace server authentication.

## Storage and backup flow

```mermaid
flowchart LR
  PG[PostgreSQL] -->|data/WAL| Volume[(Protected durable volume)]
  PG -->|pg_dump/base backup/WAL| Backup[Backup service]
  KMS[KMS / key custody] --> Backup
  Backup --> Vault[(Encrypted restricted backup)]
  Vault --> Restore[Isolated restore rehearsal]
  Restore --> Verify[Integrity + application checks]
```

The image provides database mechanics only. Volume durability, backup
consistency, encryption, access, retention, off-site custody, restore testing,
RPO, and RTO are organization responsibilities.

## Controlled-network acquisition

```mermaid
flowchart LR
  Public[Verified public digest + evidence] --> Transfer[Controlled transfer]
  Transfer --> Gate[Malware/hash/signature policy gate]
  Gate --> Registry[Internal immutable registry]
  Registry --> Deploy[Digest-only deployment]
  Feeds[Timestamped advisory/scanner data] --> Transfer
  CA[Internal CA + trusted time] --> Gate
```

The internal digest mapping, feed age, transfer custody, CA, trusted time,
rollback availability, and registry immutability must be recorded.

## Control ownership

```mermaid
flowchart TB
  Image[Image maintainer: packages, files, entrypoint, CI evidence]
  Deployment[Deployment: DB roles, HBA/TLS, secrets, resources, backup jobs]
  Host[Host/platform: kernel, OCI runtime, SELinux, seccomp, network, logs]
  Org[Organization: policy, PKI, IAM, SIEM, incident, risk acceptance]
  Image --> System[Operating database system]
  Deployment --> System
  Host --> System
  Org --> System
```

No single component artifact establishes system control effectiveness.
