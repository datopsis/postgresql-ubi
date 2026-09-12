# Control implementation view

Generated from `compliance/oscal/component-definition.json`; do not edit.
This is component support information, not an SCTM, SSP, authorization,
assessment result, STIG certification, or compliance determination.

## ac-3: deployment-supported

The component supports PostgreSQL role, database, schema, and object authorization; the deployment defines identities and grants.

- Source requirement: NIST AC-3; SRG-APP-000033-DB-000084
- Rationale: PostgreSQL supplies authorization mechanisms but no image can choose application privileges.
- Assessment: examine role/grant policy; test denied and permitted operations; interview database owner
- Default/configurable: Bootstrap creates only the requested initial superuser and database. / Roles, memberships, ownership, default privileges, and row security are deployment data.
- Prerequisites/restart: Approved role model and application identities. / Grant changes normally take effect without container restart.
- Operational impact: Least privilege can expose undeclared application dependencies.
- Loss of protection: Superuser, ownership, or broad PUBLIC grants defeat access boundaries.
- Limitations: The image does not provision an organization-specific authorization model.
- Residual risk: Excessive grants or superuser use can bypass intended separation.
- Evidence: `docs/DEPLOYMENT.md`
- Owner/review: deployment-owner / pending-independent-review

## au-2: deployment-supported

PostgreSQL emits operational logs to container stdout; event selection and centralized audit retention are deployment functions.

- Source requirement: NIST AU-2; SRG-APP-000091-DB-000066
- Rationale: The database can emit selected events while the runtime and SIEM collect and retain them.
- Assessment: examine logging configuration; test selected events and interruption; interview SIEM owner
- Default/configurable: Server logs go to stderr with the PostgreSQL default event set. / Event classes, detail, prefix, duration, and collector behavior are configurable.
- Prerequisites/restart: Runtime log driver, capacity, access control, clock, and SIEM policy. / Most logging settings reload; collector changes may require restart.
- Operational impact: Verbose SQL logging can expose data and increase I/O and storage demand.
- Loss of protection: Disabled, dropped, uncorrelated, or mutable logs remove accountability evidence.
- Limitations: The image has no SIEM, retention, immutable storage, or organization event policy.
- Residual risk: Insufficient event selection or collector loss can leave investigation gaps.
- Evidence: `docs/RUNTIME-SECURITY.md`
- Owner/review: deployment-owner / pending-independent-review

## cm-2: image-owned

The repository fixes a minimal image baseline with locked input artifacts and restricted-runtime defaults.

- Source requirement: NIST CM-2; RHEL 9 STIG V2R9 baseline concepts; SRG-APP-000516-CTR-001325
- Rationale: The repository controls packages, files, entrypoint, metadata, and tested defaults.
- Assessment: examine locks and image manifest; test native builds and restricted runtime; interview maintainer
- Default/configurable: Digest-pinned UBI stages, exact RPM closure, no package manager metadata, nonroot runtime. / Deployment may add configuration and mounts but must not mutate the image.
- Prerequisites/restart: Verified artifact bundle and protected CI inputs. / A baseline change requires rebuild and full requalification.
- Operational impact: Minimal tooling makes interactive repair and diagnostics intentionally limited.
- Loss of protection: Mutable tags, unlocked inputs, or writable root filesystems destroy baseline identity.
- Limitations: This is a component baseline, not a RHEL host baseline or DISA-approved configuration.
- Residual risk: Host, runtime, mounted configuration, and initialized data alter the effective system baseline.
- Evidence: `docs/ARTIFACT-ACQUISITION.md`
- Owner/review: maintainer / pending-independent-review

## cp-9: inherited

The image documents consistent backup interfaces; backup execution, encryption, custody, and restore objectives are inherited.

- Source requirement: NIST CP-9; Database SRG V4R5 backup requirements
- Rationale: Only the deployment knows durability, recovery objectives, keys, media, and restore location.
- Assessment: examine backup records; test isolated restore and integrity; interview storage and recovery owners
- Default/configurable: No automatic backup service is included. / Logical, physical, WAL, snapshot, encryption, and retention design is external.
- Prerequisites/restart: Durable volume, backup system, protected keys, capacity, RPO and RTO. / Backup configuration depends on method; restore normally replaces a stopped instance.
- Operational impact: Backup and restore consume I/O, storage, time, and may require quiescence.
- Loss of protection: Untested or inaccessible recovery material eliminates recoverability.
- Limitations: Image tests demonstrate mechanics only, not organization recovery objectives.
- Residual risk: Missing, stolen, inconsistent, or untested backups can cause disclosure or irreversible loss.
- Evidence: `docs/STORAGE.md`
- Owner/review: organization-owner / pending-independent-review

## ia-5: deployment-supported

The image requires a bootstrap secret and defaults PostgreSQL passwords and host rules to SCRAM-SHA-256; lifecycle policy is external.

- Source requirement: NIST IA-5; SRG-APP-000171-DB-000074; PostgreSQL 18 password authentication
- Rationale: The image enforces safe bootstrap transport and hashing; the organization creates and rotates secrets.
- Assessment: examine secret and HBA configuration; test missing secret and SCRAM login; interview secret owner
- Default/configurable: Secret file required on first initialization; SCRAM-SHA-256 selected; trust rejected. / External HBA and server configuration can change authentication and iteration count.
- Prerequisites/restart: Runtime secret service with correct ownership, mode, rotation, and audit. / HBA reload is sufficient; role password rotation is online; bootstrap secret is initialization-only.
- Operational impact: Rotation and stronger hashing can affect clients and authentication latency.
- Loss of protection: Trust, cleartext network password use, leaked secret files, or stale roles enable compromise.
- Limitations: No password breach-list service, MFA, or enterprise identity provider is included.
- Residual risk: Weak, reused, exposed, or unrotated passwords remain possible.
- Evidence: `tests/runtime-security.sh`
- Owner/review: deployment-owner / pending-independent-review

## ir-4: inherited

The repository provides withdrawal and evidence-preservation procedures; incident command and notification are organization-owned.

- Source requirement: NIST IR-4; NIST SP 800-53A examine/test/interview method
- Rationale: A public component maintainer cannot operate a consumer incident response program.
- Assessment: examine plan and rehearsal; test contact and quarantine path; interview incident owner
- Default/configurable: Private reporting and maintainer withdrawal procedures are documented. / Consumer severity, legal notification, evidence, and containment plans are external.
- Prerequisites/restart: Named responders, monitored contacts, registry authority, backups, and legal policy. / Containment may stop service; recovery uses a new qualified digest and rotated credentials.
- Operational impact: Containment and evidence preservation can interrupt database availability.
- Loss of protection: Moving tags, deleting evidence, or reusing credentials compromises recovery confidence.
- Limitations: The maintainer does not know consumer contacts, data, law, or infrastructure.
- Residual risk: Delayed coordination can expand compromise and evidence loss.
- Evidence: `docs/INCIDENT-RESPONSE.md`
- Owner/review: organization-owner / pending-independent-review

## sc-13: research-required

Cryptographic mechanisms are inventoried, but no FIPS validation claim is made for this image or PostgreSQL configuration.

- Source requirement: NIST SC-13; SRG-APP-000179-DB-000114; RHEL 9 STIG V2R9
- Rationale: A claim requires exact library linkage, provider mode, architecture, runtime context, and applicable CMVP certificate.
- Assessment: examine binaries, providers and CMVP records; test each architecture/mode; interview cryptographic authority
- Default/configurable: No FIPS or validated-cryptography claim. / Host mode, OpenSSL providers, PostgreSQL TLS, SCRAM, checksums, and signing are separate boundaries.
- Prerequisites/restart: Exact release digest and architecture plus verified module, provider, host, and CMVP evidence. / Mode/provider/TLS changes can require host and database restart and requalification.
- Operational impact: Approved algorithms and provider modes may reduce compatibility or performance.
- Loss of protection: Unapproved providers, algorithms, key handling, or boundary changes invalidate a claim.
- Limitations: No applicable CMVP certificate or tested end-to-end mode is established.
- Residual risk: Operators may mistake UBI origin, TLS, or host FIPS mode for validated image cryptography.
- Evidence: `docs/CRYPTOGRAPHIC-BOUNDARY.md`
- Owner/review: maintainer / pending-independent-review

## sc-8: deployment-supported

The image supports PostgreSQL TLS but leaves certificate issuance, trust, client verification, and ingress enforcement to deployment.

- Source requirement: NIST SC-8; SRG-APP-000441-DB-000378
- Rationale: TLS capability is inside PostgreSQL; certificates and network enforcement are deployment-specific.
- Assessment: examine certificate/HBA/client policy; test TLS and plaintext rejection; interview PKI owner
- Default/configurable: TLS is not enabled without deployment-provided key, certificate, HBA, and configuration. / TLS versions, ciphers, CA, client certificates, HBA and client sslmode are configurable.
- Prerequisites/restart: Protected server key, valid certificate chain, trusted time, DNS, and client trust. / Initial enablement requires restart; certificate/configuration reload behavior must be rehearsed.
- Operational impact: Strict verification can reject misnamed, expired, or untrusted certificates.
- Loss of protection: Plain host records, sslmode disable/prefer, or key compromise remove transport assurance.
- Limitations: TLS support is not a FIPS validation or proof of client policy.
- Residual risk: Clients can be spoofed or traffic exposed if TLS or verification is optional.
- Evidence: `tests/tls.sh`
- Owner/review: deployment-owner / pending-independent-review

## si-2: image-owned

The project monitors suppliers, locks exact inputs, scans both architectures, and defines time-bound remediation and withdrawal decisions.

- Source requirement: NIST SI-2; SRG-APP-000456-DB-000390
- Rationale: Maintainers own component input monitoring, rebuild, qualification, and release withdrawal.
- Assessment: examine advisories, scans and exceptions; test rebuild/withdrawal; interview triage owner
- Default/configurable: Fixed High/Critical findings block; scheduled monitoring and two scanners are configured. / Exceptions require exact digest/architecture, approval, expiry and rescan trigger.
- Prerequisites/restart: Current PGDG, PostgreSQL, Red Hat and scanner data plus monitored private reports. / Correction requires a new immutable image digest and deployment rollout.
- Operational impact: Urgent withdrawal or update can interrupt planned change windows.
- Loss of protection: Stale databases, blanket ignores, moving tags, or bypassed qualification defeat remediation.
- Limitations: Scanners do not prove reachability, absence of design flaws, or deployment patching.
- Residual risk: Unknown, unfixed, disputed, or deployment-specific exposure can remain.
- Evidence: `docs/VULNERABILITY-MANAGEMENT.md`
- Owner/review: maintainer / pending-independent-review

## sr-4: image-owned

The build verifies publisher signatures, checksums, source-to-binary mappings, exact package closures, SBOMs, provenance, and release signatures.

- Source requirement: NIST SR-4; Container Platform SRG supply-chain requirements
- Rationale: Repository workflows own acquisition verification and evidence for produced images.
- Assessment: examine locks/provenance/signatures; test tampered input and independent verification; interview release owner
- Default/configurable: Exact hashes, fingerprints, actions, scanners, native architectures, and immutable release identity. / Any supplier, key, package, action, tool, or base closure change requires reviewed lock update.
- Prerequisites/restart: Protected branch, trusted GitHub identities, supplier keys, registry, OIDC and evidence retention. / Input changes produce a new digest; consumers must explicitly roll out that digest.
- Operational impact: Fail-closed verification can delay builds and releases.
- Loss of protection: Unverified mirrors, mutable refs, compromised keys/runners, or missing evidence break traceability.
- Limitations: Provenance establishes recorded build inputs, not supplier or CI infallibility.
- Residual risk: Supplier, signing-key, CI runner, registry, or evidence systems can still be compromised.
- Evidence: `docs/RELEASE.md`
- Owner/review: maintainer / pending-independent-review
