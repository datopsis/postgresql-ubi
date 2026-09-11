# First-release roadmap

This roadmap is the release gate for the first supported `postgresql-ubi`
image. The immediate objective is a small, operationally usable PostgreSQL 18
image without postponing controls that are difficult to retrofit safely around
database credentials, durable state, artifact provenance, or release identity.

A checked item requires reviewable evidence in a pull request, workflow run,
release asset, qualification record, or external-platform test record. A green
job alone is not sufficient where an item also requires human analysis, an
external environment, a support decision, or acceptance of residual risk.

## Evidence lifecycle

Evidence has three levels:

1. **Development evidence** comes from a proposed revision or pull request.
2. **Integration evidence** comes from the exact revision merged to `main`.
3. **Release-candidate evidence** is regenerated after the last
   image-affecting change and bound to the candidate commit, image digest,
   architecture, artifact-lock digest, configuration profile, scanner inputs,
   and platform versions.

Changing PostgreSQL or UBI inputs, the complete RPM closure, image contents,
entrypoint behavior, authentication or storage defaults, release workflow,
scanner content, SCAP tailoring, or a qualification procedure invalidates the
affected release-candidate evidence. Historical results remain useful for
comparison but cannot qualify the changed candidate.

Create and maintain `docs/QUALIFICATION.md` as the durable evidence ledger. It
must distinguish automated evidence from human review and external-platform
qualification, and it must never contain credentials, database contents, or
private environment details.

## Approved first-release boundary

These positions were approved as the scope to qualify. They are not current
support claims until the corresponding qualification gates close.

Use these terms consistently:

- **Supported** means an exact image digest, architecture, configuration
  profile, host/runtime combination, and support period passed the documented
  gates and is named by the release support statement.
- **Compatible** means limited evidence demonstrates interoperability without a
  production-support commitment for that combination.
- **Preview/unqualified** means fixtures or guidance exist but required review,
  operational evidence, or platform qualification is incomplete.
- **Unsupported** means deliberately outside the first-release boundary.

| Area | Approved first-release position |
| --- | --- |
| PostgreSQL | Maintain major 18; select the current reviewed 18.x minor only after image-affecting work is complete. |
| UBI | UBI 9 Minimal builder and UBI 9 Micro runtime, both by reviewed manifest digest. |
| Architectures | Support native `linux/amd64` and `linux/arm64`. |
| Primary runtime | Qualify rootless Podman on an exact RHEL 9 host/runtime baseline with SELinux enforcing and cgroup v2. |
| Docker | Retain native GitHub Actions compatibility evidence; do not imply the same production-support boundary as qualified Podman. |
| OpenShift | Provide restricted-SCC arbitrary-UID fixtures and procedures; claim support only if an exact OpenShift release is qualified, otherwise mark it preview/unqualified. |
| Authentication | Require a non-empty initialization secret and SCRAM-SHA-256 for network clients; provide no remote `trust` escape hatch. |
| TLS | Qualify an operator-provided TLS 1.2/1.3 server profile with read-only mounted key, certificate chain, and trust material; do not generate production keys in the image. |
| Storage | Support one PostgreSQL instance using one operator-provisioned durable data volume; require tested backup and restoration. |
| High availability | Streaming replication, failover orchestration, pooling, and multi-node HA are outside the first image release. |
| Upgrades | Support reviewed PostgreSQL 18 minor updates. Reject other-major data directories; major upgrades remain an operator-planned `pg_upgrade` or dump/restore operation. |
| Extensions | Ship only the selected PGDG server/client closure. Additional extensions, including `pgaudit`, require separate provenance, configuration, and maintenance decisions. |
| Controlled networks | Document verified acquisition, transfer, mirrored deployment, local trust, vulnerability-data refresh, update, and rollback procedures. |
| FIPS | Make no FIPS validation or approved-mode claim without a separately defined and evidenced cryptographic module and operational environment. |
| STIG/SCAP | Publish exact tailored image-filesystem results; make no STIG certification, broad compliance, or system-authorization claim. |
| Registry | Publish the first immutable release to GHCR only. |

Logical backup and restore are inside the first-release boundary. Physical
backup, WAL archiving, point-in-time recovery, replication, and failover must
have clear ownership and safe guidance, but are not claimed as image-managed
services in the first release.

## Immediate first-release sequence

Work proceeds in this dependency order:

1. **Complete:** approve the release/support boundary and evidence schema.
2. **Complete:** implement the complete artifact lock, verified out-of-build acquisition,
   and network-disabled assembly.
3. Close the database security, storage, lifecycle, TLS, logging, backup,
   restore, and upgrade test matrix.
4. Add the release pipeline and remaining supply-chain controls.
5. Complete the cybersecurity requirement analysis, threat model, control
   artifacts, tailored SCAP evidence, and vulnerability policy.
6. Qualify rootless Podman and the selected operational profile on an exact
   host, then make explicit Docker, OpenShift, and disconnected-environment
   decisions.
7. Freeze current upstream inputs and regenerate all release-candidate evidence.
8. Rehearse and execute the immutable signed publication, verify it by digest,
   and publish the support statement.

Packages may be prepared in parallel only where they do not assume an unfrozen
package closure or make a support claim before qualification.

## Existing foundation

- [x] Define the repository, image name, maintained PostgreSQL major line,
  version format, contribution process, security-reporting route, and initial
  support boundary.
- [x] Add digest-pinned UBI Minimal and UBI Micro stages and exact,
  architecture-specific PostgreSQL 18.6 RPM URLs, SHA-256 digests, and PGDG
  signing keys.
- [x] Add a package-manager-free UBI Micro runtime that defaults to non-root
  UID `26`, supports an OpenShift-style arbitrary UID in group `0`, and runs
  with a read-only root filesystem, no capabilities, and
  `no-new-privileges`.
- [x] Require exactly one initialization password source for an empty data
  directory, configure SCRAM-SHA-256 network authentication, and reject a data
  directory from another PostgreSQL major version.
- [x] Test initialization, authenticated SQL, persistence across container
  replacement, graceful shutdown, fixed and arbitrary UIDs, restricted runtime
  settings, absent credentials, and an incompatible major version.
- [x] Add native AMD64 and ARM64 CI with linting, configuration scanning,
  CodeQL, Trivy, Syft SPDX inventories, Grype, and an aggregate architecture
  gate.
- [x] Enable secret scanning, push protection, dependency alerts and security
  updates, private vulnerability reporting, and OpenSSF Scorecard.

These checks are development and integration evidence. They must run again for
the frozen candidate and do not by themselves close the gates below.

## Package 1: release contract and evidence ownership (complete)

- [x] Review and approve the first-release boundary, including the
  exact treatment of TLS, Docker, OpenShift, logical backup, physical recovery,
  extensions, FIPS, SCAP, and controlled-network operation.
- [x] Reconcile `README.md`, `docs/SUPPORT.md`, `docs/VERSION.md`,
  `SECURITY.md`, operator documentation, and issue templates with the approved
  boundary. Remove stale statements such as planned native CI after evidence
  already exists.
- [x] Define the initial support period, PostgreSQL and UBI update cadence,
  vulnerability-response targets, supersession window, withdrawal procedure,
  and end-of-support policy.
- [x] Define `docs/QUALIFICATION.md` fields for commit, image and lock digests,
  architecture, PostgreSQL/PGDG/UBI inputs, runtime and host versions,
  configuration profile, scanner/tool/database versions, result, limitations,
  evidence level, artifact location, reviewer, and retention period.
- [x] Assign owners for image maintenance, PostgreSQL security triage, UBI
  triage, signing-key changes, release approval, registry administration,
  vulnerability reports, and release evidence.
- [x] Inventory proposed badges and publish only claims backed by current,
  inspectable evidence with an owner and removal condition.

**Exit evidence:** `docs/SUPPORT.md`, `docs/MAINTENANCE.md`,
`docs/QUALIFICATION.md`, and the badge inventory in
`docs/REPOSITORY-GOVERNANCE.md` define the approved boundary, accountable
owners, and required evidence without turning planned qualification into a
current support claim.

## Package 2: artifact lock and hermetic assembly

Implement the complete contract in `docs/ARTIFACT-ACQUISITION.md`.

- [x] Create schema-validated AMD64 and ARM64 lock manifests containing both UBI
  references and manifest digests, every PostgreSQL and UBI RPM NEVRA, byte
  size, SHA-256, architecture, approved full signing fingerprint, source RPM,
  artifact-source identifier, and lock schema version.
- [x] Record and review the entire installed RPM closure rather than only the
  three top-level PostgreSQL RPMs. Investigate unexpected package, file,
  setuid/setgid, world-writable, executable, or architecture differences.
- [x] Implement a dedicated lock-update command and workflow. Resolution is an
  explicit review activity; ordinary pull-request, `main`, and release builds
  must never recalculate the closure or select `latest`.
- [x] Acquire only locked artifacts outside the container build. Enforce
  approved hosts and redirects, bounded retries/timeouts, least-privilege
  credentials when needed, sanitized logs, and cleanup of ephemeral staging.
- [x] Verify size, SHA-256, RPM signature and approved full fingerprint, NEVRA,
  source-RPM correspondence, architecture, base-image platform, and manifest
  digest before admitting a bundle to assembly.
- [x] Reject tampered, unsigned, unapproved-key, wrong-version,
  wrong-architecture, duplicate, missing, and unexpected artifacts, malformed
  locks, wrong base digests, and source-RPM mismatches.
- [x] Make local, pull-request, `main`, and candidate assembly consume the same
  verified bundle with networking and image pulling disabled and without
  repository configuration or dependency resolution.
- [x] Prove that repository addresses, credentials, signing keys, private CA
  material, caches, and acquisition logs do not enter image files, layers,
  history, labels, SBOMs, or provenance.
- [x] Define signing-key rotation, revocation, mirror substitution, bundle
  transfer, lock rollback, and emergency rebuild procedures. A mirror must
  preserve publisher-signed bytes unless a separately approved trust model is
  documented.
- [x] Record source availability, redistribution terms, trademark boundaries,
  and update ownership for every runtime component.

**Exit evidence:** a clean build succeeds from only the reviewed bundle with
network and pulls disabled, and every negative bundle test fails closed.

Completed by CI run
[`34608785089`](https://github.com/datopsis/postgresql-ubi/actions/runs/34608785089)
for commit `3114702788c0ac67660a3526a7078fe6457273b0`. Native AMD64 and ARM64
jobs acquired and verified their committed locks, assembled with an empty build
cache and build networking disabled, passed restricted-runtime smoke tests,
Trivy and Grype gates, generated SPDX SBOMs and build provenance, and proved
acquisition material absent from retained image and assurance artifacts. The
locks contain the complete reviewed closures: 161 binary RPMs and 111 source
RPMs for AMD64, and 162 binary RPMs and 111 source RPMs for ARM64. The five
artifact test groups passed their malformed, tampered, unsigned,
unapproved-key, wrong-version, wrong-architecture, duplicate, missing,
unexpected, wrong-base, and source-mismatch cases fail closed.

## Package 3: database security and runtime contract

### Initialization, identity, and authentication

- [ ] Threat-test both password interfaces for empty values, simultaneous
  variables, unreadable files, symlinks, permissions, unusual characters,
  command-line exposure, environment inspection, logs, errors, core dumps, and
  persistence after initialization. Document the remaining environment-variable
  exposure and prefer secret-file mounts.
- [ ] Test interrupted and concurrent first initialization, a non-empty
  directory without `PG_VERSION`, partial initialization residue, wrong
  ownership, read-only storage, full storage, and restart after each failure.
  Fail closed with actionable diagnostics and never silently reinitialize data.
- [ ] Review the generated `pg_hba.conf` and `postgresql.conf` line by line.
  Prove remote password authentication is SCRAM, local trust is limited to the
  container-local socket boundary, password encryption remains SCRAM, and
  configuration precedence cannot silently weaken these defaults.
- [ ] Document role and database creation, password rotation after
  initialization, superuser ownership, least-privilege application roles, and
  why initialization environment variables are not a general account-management
  interface.
- [ ] Decide whether init scripts are deliberately unsupported for v1 or add a
  narrowly specified, ordered, failure-safe interface with tests for ownership,
  secrets, retries, and partial execution.

### Durable storage and lifecycle

- [ ] Publish detailed, executable deployment playbooks for every v1 use case:
  fixed UID and arbitrary UID, rootless Podman and Docker/Compose, named volumes
  and SELinux-labeled bind mounts, TLS and intentionally isolated non-TLS
  profiles, mounted configuration, controlled-network transfer, backup/restore,
  minor update, rollback, failure recovery, and teardown. Each playbook must
  state prerequisites, trust and ownership boundaries, every deployment step,
  expected verification evidence, security-sensitive alternatives, failure
  diagnostics, and data-preserving removal steps.
- [ ] Document named-volume and bind-mount ownership for UID `26:0` and
  arbitrary UID/group `0`, including SELinux labels, NFS root-squash, CSI/PVC
  behavior, filesystem permissions, and safe failure diagnostics.
- [ ] Prove data checksums are enabled and test clean shutdown, termination
  during writes, forced termination, crash recovery, restart with a large WAL,
  PID/socket cleanup, and container replacement without data loss.
- [ ] Test disk-full, inode-full, bounded `/tmp`, insufficient shared memory,
  low file-descriptor/PID limits, memory pressure/OOM, connection exhaustion,
  and startup under recovery. Document safe resource, `shm_size`, timeout, and
  termination-grace guidance without claiming universal sizing values.
- [ ] Define logical `pg_dump`/`pg_restore` backup and restore procedures,
  encryption and access requirements, retention/immutability ownership, and a
  scheduled isolated restoration test with measured recovery time and data
  validation.
- [ ] Document ownership and safe starting points for physical backup,
  `pg_basebackup`, WAL archiving, point-in-time recovery, and storage snapshots.
  Do not imply these are complete merely because the binaries are present.
- [ ] Test a PostgreSQL 18 minor update against preserved data, application
  compatibility fixtures, backup/restore, and rollback constraints. Retain the
  previous digest and explain that downgrading database files is not assumed
  safe.
- [ ] Keep other-major data directories rejected and publish a major-upgrade
  decision tree for `pg_upgrade` versus logical dump/restore without claiming a
  major upgrade has been qualified.

### TLS, configuration, logging, and observability

- [ ] Provide a tested TLS 1.2/1.3 profile using operator-mounted server key,
  certificate chain, and trust store. Enforce key ownership and permissions;
  test correct trust, hostname failure, untrusted chain, expired/not-yet-valid
  certificates, clear-text policy, renewal, rotation, and rollback using an
  ephemeral CA with no committed private material.
- [ ] Document and test the v1 exclusion of client-certificate authentication
  and certificate-to-role mapping. Do not imply mTLS support from a server-TLS
  test; qualifying this later requires a new support decision and profile.
- [ ] Define the supported configuration interface, validation command,
  precedence, reload/restart behavior, immutable defaults, rollback, and
  diagnostics. Test mounted configuration and command-line overrides for both
  valid and security-weakening cases.
- [ ] Keep database logs on stdout/stderr and provide structured collection
  guidance for connection, authentication, checkpoint, recovery, and shutdown
  events. Test secret, SQL-value, and personally identifiable information
  exclusion; explain why broad statement logging can itself expose sensitive
  data.
- [ ] Document the v1 deferral of PostgreSQL audit extensions. Adding one later
  requires new RPM provenance, configuration, performance, log-volume,
  vulnerability-lifecycle, and support decisions.
- [ ] Distinguish startup, readiness, liveness, and external transaction
  monitoring. Keep probes low privilege, bounded, non-sensitive, and resistant
  to load-induced restart loops.
- [ ] Compare the candidate with the matching official PostgreSQL image:
  entrypoint behavior, environment interface, users, storage paths, packages,
  ports, health semantics, image size, and documented compatibility gaps.

**Exit evidence:** positive and negative AMD64/ARM64 tests cover every claimed
database interface, security default, storage transition, and lifecycle path.

## Package 4: CI, updates, and release supply chain

- [ ] Add tests for release-tag syntax, real UTC dates and sequences,
  PostgreSQL/UBI/lock matching, annotated tags, protected-`main` ancestry,
  changelog state, and rejection of mutable, malformed, reused, moved, or
  mismatched tags.
- [ ] Add a least-privilege, non-cancelling release workflow that publishes only
  the immutable release and commit tags, produces the native AMD64/ARM64
  manifest, records complete OCI metadata, and separates build, scan, approval,
  signing, and release permissions.
- [ ] Generate architecture-specific and manifest-level SBOM/provenance
  attestations, a downloadable complete SPDX SBOM, scan results, lock and source
  provenance, image configuration, and verification instructions bound to the
  published digest.
- [ ] Sign the image digest and complete SPDX attestation keylessly with GitHub
  OIDC/Cosign, retain verification bundles, and test issuer, identity, digest,
  and attestation-policy verification without relying on a mutable tag.
- [ ] Retain full Trivy and Grype findings, including unfixed and lower-severity
  inventory for human triage. Scanner operational errors, missing inventories,
  architecture mismatches, or absent evidence always block.
- [ ] Add monitored update proposals for PostgreSQL releases, PGDG RPMs and
  signing keys, UBI manifests and dependency locks, GitHub Actions, scanner
  engines/databases, Cosign, ComplianceAsCode, and other assurance tooling.
- [ ] Define the UBI-only emergency rebuild path and response target so a base
  security update does not wait for a PostgreSQL release.
- [ ] Audit workflow permissions, immutable action references, artifact
  attestations, cache trust, fork behavior, expression injection, artifact
  overwrite/extraction risks, OIDC scope, token persistence, and environment
  protections.
- [ ] Define release-evidence retention and backup. Release evidence must outlive
  workflow artifact expiry and remain available for incident response and
  verification throughout the support and supersession period.
- [ ] Define failed-candidate handling: no failed digest is signed or announced;
  a partially published tag/digest is quarantined or removed and never reused.

**Exit evidence:** a rehearsal proves the exact reviewed candidate can be
published, scanned, attested, signed, and independently verified with only the
documented least privileges.

## Package 5: cybersecurity engineering and review package

### Authoritative requirements and control ownership

- [ ] Create an authoritative source register recording publisher, title,
  release, date, retrieval date, URL, SHA-256, current/superseded status, and
  license or redistribution handling.
- [ ] Analyze applicable NIST SP 800-53 Rev. 5 and SP 800-53A Rev. 5, the DISA
  Database SRG and Container Platform SRG, current RHEL 9 STIG content, and
  active PostgreSQL-distribution STIGs. Product-specific STIG commands and
  assumptions are references only until proven applicable to PGDG PostgreSQL.
- [ ] Classify every analyzed requirement exactly once as image-owned,
  deployment-supported, inherited, not applicable, unsupported, or research
  required, with rationale, residual risk, evidence, owner, and review status.
  Require independent review of adopted, excluded, unsupported, and
  not-applicable decisions.
- [ ] Publish a schema-valid NIST OSCAL Component Definition as the canonical
  component artifact and deterministically generate an SCTM-importable CSV and
  human-readable control implementation view from it. Do not represent these as
  a completed system SCTM, SSP, authorization, or assessor decision.
- [ ] Give each supported control an examine/test/interview assessment method,
  default and configurable state, prerequisites, restart behavior, operational
  impact, loss-of-protection statement, limitations, residual risk, evidence
  pointer, and image/deployment/host/organization owner.

### Threats, hardening, and compliance evidence

- [ ] Publish architecture, build/assurance pipeline, runtime data-flow,
  credential and TLS trust, storage/backup, controlled-network, and
  control-ownership diagrams.
- [ ] Publish a threat model covering artifact and key substitution, CI/cache
  and runner compromise, malicious pull requests, tag/registry replacement,
  evidence tampering, runtime identity, arbitrary UID, secret disclosure,
  authentication downgrade, configuration injection, exposed listeners,
  untrusted clients, SQL abuse, denial of service, shared memory and resource
  exhaustion, storage tampering/corruption, backup theft or failed restoration,
  TLS key/trust compromise, sensitive logs, vulnerable dependencies, update
  failure, rollback, and decommissioning.
- [ ] Map every threat to mitigations, validation, owner, limitations, and open
  risk. A clean vulnerability scan does not close design or abuse-case threats.
- [ ] Run pinned OpenSCAP and ComplianceAsCode discovery against a
  root-owner-preserving, never-executed export of each architecture image.
  Select only image-owned rules, document every inclusion/exclusion and rule
  rationale, publish tailoring, distinguish failures from not-applicable and
  deployment-owned controls, and make scanner execution errors blocking.
- [ ] Keep SCAP findings report-only until the profile and false-positive
  process receive security review and an explicit blocking policy is approved.
  State the exact filesystem evidence boundary and make no host, deployment,
  STIG-certification, or compliance claim.
- [ ] Define the cryptographic boundary for PostgreSQL password hashing, TLS,
  checksums, signing, and the host/runtime. Identify actual linked libraries,
  module versions, provider/mode behavior, architectures, and any applicable
  CMVP certificate before making a claim. UBI, RHEL FIPS mode, TLS 1.2/1.3, or
  Cosign alone does not establish FIPS validation for the database image.

### Vulnerability, incident, and exception management

- [ ] Publish a vulnerability process covering PostgreSQL/PGDG and Red Hat
  advisory precedence, scanner disagreement, package/source-package grouping,
  reachability and exposure, fixed versus unfixed findings, patch SLAs,
  disclosure coordination, emergency rebuilds, and periodic reassessment.
- [ ] Require every suppression or accepted finding to name the exact digest
  and architecture, advisory, affected component, vendor status, rationale,
  compensating control, owner, approval, expiry, and rescan trigger. Never use a
  blanket or permanent ignore merely to make a release pass.
- [ ] Confirm the private vulnerability route is monitored and rehearse the
  response path without filing a real report or exposing sensitive details.
- [ ] Publish incident, containment, credential/certificate rotation, forensic
  evidence, backup recovery, customer notification, release withdrawal,
  registry quarantine, and lessons-learned responsibilities.
- [ ] Document network policy, firewall/ingress, DNS, secret service, SELinux,
  seccomp, monitoring/SIEM, log retention and disposal, backup encryption and
  access, resource limits, time synchronization, controlled transfer, and
  decommissioning responsibilities that remain outside the image.

**Exit evidence:** a security reviewer can trace every claimed component
control from an authoritative source through ownership, implementation,
assessment method, evidence, limitation, and residual risk.

## Package 6: deployment and platform qualification

- [ ] Publish an exact support matrix for architecture, RHEL/kernel, Podman,
  OCI runtime, SELinux, cgroup version, rootless identity, Docker compatibility,
  OpenShift, TLS profile, storage type, backup/restore profile,
  connected/disconnected operation, SCAP, and FIPS claims.
- [ ] Provide and qualify a rootless Quadlet deployment on the selected RHEL 9
  baseline: dedicated account, subordinate IDs, lingering, boot, health,
  restart throttling, bounded tmpfs, read-only root, capability drop,
  `no-new-privileges`, seccomp, SELinux labels, durable storage, graceful stop,
  update, rollback, and decommissioning.
- [ ] Qualify journald/stdout collection, event fields, time correlation,
  access control, authenticated forwarding, interruption, rate/capacity limits,
  storage pressure, retention, integrity protection, and disposal without
  credential or SQL-data leakage.
- [ ] Test the complete supported profile with positive, negative,
  restricted-runtime, backup/restore, upgrade, rollback, load, resource
  exhaustion, storage, recovery, TLS, logging, monitoring, and incident cases
  on each claimed architecture/platform combination.
- [ ] Retain native Docker compatibility evidence separately from the supported
  Podman baseline and document engine-specific volume, tmpfs, signal, health,
  user, networking, and security-option behavior.
- [ ] Provide restricted-SCC OpenShift fixtures using arbitrary UID/group `0`,
  a PVC, Secret, ConfigMap, Service, probes, resource limits, NetworkPolicy, and
  safe termination. Qualify an exact release without `anyuid`, host paths,
  added capabilities, or privilege; otherwise state preview/unqualified.
- [ ] Document connected and controlled-network deployment: verify and mirror
  the exact image digest and release evidence, map internal registry digests,
  refresh vulnerability/advisory data with age recorded, manage internal CA and
  time trust, transfer updates, and rehearse rollback without public access.
- [ ] Publish `docs/PRODUCTION.md` covering identity, secrets, roles,
  configuration, TLS, network exposure, storage, backups/restores, monitoring,
  alerting, resources, capacity, patching, upgrades, rollback, incidents,
  controlled networks, and decommissioning.
- [ ] Define go-live evidence for the exact image/configuration digest,
  platform, storage, restored backup, capacity and failure results, current
  vulnerability decisions, controls, alert routing, contacts, exceptions, and
  runbooks.

**Exit evidence:** the exact candidate passes the complete runbook on the named
supported host, and every other platform claim is explicitly classified.

## Package 7: frozen release-candidate qualification

- [ ] After all planned image/configuration changes, select the current reviewed
  PostgreSQL 18 minor, PGDG builds and signing keys, compatible UBI 9 Minimal
  and Micro manifests, complete RPM locks, and assurance-tool versions.
- [ ] Review PostgreSQL release notes, security announcements, PGDG packaging,
  Red Hat errata, source RPMs, key status, UBI lifecycle, and why no newer
  relevant reviewed input is being selected.
- [ ] For PostgreSQL 18.6, disposition every security and migration note,
  including the required configuration adjustments and data-cleanup checks,
  the `output_plugin_libraries` restriction, affected extension indexes, and
  upgrades from a release earlier than 18.2. Prove which notes apply to a fresh
  cluster and which apply to a supported 18.x update; do not treat a
  dump/restore-not-required statement as no-action-required.
- [ ] Rebuild both architectures from clean acquisition and empty build caches.
  Compare packages, files, permissions, layers, size, OCI configuration, SBOMs,
  provenance, and scanner results; explain every unexpected delta.
- [ ] Confirm the runtime remains non-root, arbitrary-UID compatible,
  package-manager/downloader-free, capability-free, read-only-root compatible,
  and limited to documented writable paths and listeners.
- [ ] Review every fixed and unfixed Trivy/Grype finding using authoritative
  PostgreSQL/PGDG and Red Hat context. Resolve it, document a time-bounded
  acceptance, or delay the release.
- [ ] Complete the SPDX package/license review, embedded notices, source
  availability, UBI and PostgreSQL redistribution terms, trademarks, and
  `THIRD_PARTY_NOTICES.md`.
- [ ] Audit actual repository settings: protected `main`, required up-to-date
  checks, conversation resolution, force-push/deletion blocks, Actions token
  defaults, immutable Actions policy, environments, secret scanning, push
  protection, Dependabot, CodeQL, Scorecard, private reporting, and package
  visibility.
- [ ] Regenerate native architecture, hermetic build, runtime, TLS,
  backup/restore, upgrade, rootless Podman, Docker compatibility,
  controlled-network, SCAP, and cyber-control evidence for the exact candidate.
- [ ] Review every document and command from a clean clone. Verify no secret,
  generated database, private key, scanner cache, SBOM, SARIF, or private
  endpoint entered Git or public evidence.
- [ ] Complete `docs/QUALIFICATION.md` with exact evidence links, results,
  limitations, reviewers, expirations, and open risks. No image-affecting change
  may follow without invalidating and regenerating affected evidence.

**Exit evidence:** the release pull request identifies one immutable candidate,
all inputs and findings, every qualified claim, accepted risks, and the complete
evidence chain needed for approval.

## Package 8: release rehearsal and signed first publication

- [ ] Implement an active `main` ruleset requiring pull requests, resolved
  conversations, up-to-date `lint`, `configuration security`, aggregate
  `image`, and CodeQL checks, with force pushes/deletion blocked and no routine
  bypass. Set review requirements consistent with available independent
  maintainers and explicitly record any single-maintainer residual risk.
- [ ] Add a release-tag ruleset matching `docs/VERSION.md` only after the
  workflow actor and creation procedure are proven. Block tag updates and
  deletion and prevent release-tag reuse.
- [ ] Rehearse tag validation and the complete workflow from an untagged or
  disposable candidate. Verify least privilege, environment approval, native
  manifest assembly, scans, SBOM/provenance, signing, attestations, evidence
  retention, failed-candidate quarantine, and independent verification.
- [ ] Select the first release identifier, convert `Unreleased` changelog
  entries into the matching dated section, and open a release pull request that
  names the candidate digest, support boundary, evidence ledger, findings,
  accepted risks, rollback, and release/incident contacts.
- [ ] Obtain independent security and release review for the first publication
  without bypassing required checks, then merge the exact approved commit to
  protected `main`.
- [ ] Create the annotated immutable tag from that exact `main` commit and watch
  publication through manifest validation, scanning, attestation, signing, and
  GitHub Release creation. Never rerun by moving or reusing the tag.
- [ ] Publish only the complete immutable release tag and immutable
  `sha-<short-commit>` tag to public GHCR. Do not initially publish `latest`,
  `18`, or `18.x` mutable tags.
- [ ] Verify the public digest on native AMD64 and ARM64: platform descriptors,
  PostgreSQL version and SQL behavior, OCI labels, package inventory, SBOM,
  provenance, lock digest, Cosign identity/signature/attestation, release assets,
  documentation links, and rollback instructions.
- [ ] Publish release notes and `docs/SUPPORT.md` stating exact supported and
  compatible combinations, security contacts and targets, known limitations,
  accepted risks, upgrade/backup requirements, evidence locations, and
  end-of-support/supersession dates.
- [ ] Refresh Scorecard and GitHub security views after publication, confirm the
  GHCR package is public and linked to the repository, and archive durable
  verification evidence outside short-lived workflow artifacts.

**Exit evidence:** the public GHCR digest, GitHub Release, signature bundle,
attestations, SBOM, qualification ledger, and support statement all identify
the same approved commit and artifact.

## Assurance completeness gate

Before release, record any intentionally omitted item with a PostgreSQL-specific
rationale and owner. The final review covers evidence lifecycle, support
semantics, qualification ledger, architecture and trust boundaries, artifact
locks and hermetic assembly, native architecture evidence, rootless runtime and
platform qualification, authentication, TLS and cryptographic boundaries,
durable storage, backup/restore, recovery and upgrades, authoritative
requirement analysis, control ownership and OSCAL export, tailored SCAP,
vulnerability and exception management, licensing, controlled networks,
production go-live evidence, failed-candidate handling, release rehearsal,
rollback, incident response, decommissioning, and evidence retention.

## Deliberately deferred until after the first release

Each deferred capability needs its own threat boundary, provenance, test
matrix, operational guidance, and maintenance commitment before it is claimed.

- [ ] Streaming replication, synchronous replication, automated failover,
  connection pooling, and multi-node high availability.
- [ ] Qualified physical backup/WAL archive/PITR products and storage-provider
  integrations beyond the v1 ownership guidance.
- [ ] PostgreSQL major-version upgrade qualification and cross-major rollback.
- [ ] Additional extensions such as `pgaudit`, PostGIS, logical-decoding
  plugins, foreign data wrappers, and third-party authentication modules.
- [ ] Client-certificate role mapping if it is not selected for the v1 TLS
  profile.
- [ ] Broad Kubernetes support beyond the explicit OpenShift decision.
- [ ] Performance, concurrency, long-duration soak, and HA capacity baselines
  beyond the single-instance safety tests required for v1.
- [ ] Mutable convenience tags and additional registries.
- [ ] A FIPS-specific build and qualification profile, if a defensible module
  and operational boundary can be established.
