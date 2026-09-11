# Release qualification evidence

No release candidate has been qualified. This file defines the evidence record
that every candidate and supported release must complete. Placeholder text,
development CI, or an omitted field is not passing evidence.

## Evidence levels

- **Development** evidence is produced for a proposed revision or pull request.
- **Integration** evidence is produced for the exact revision merged to
  `main`.
- **Release-candidate** evidence is regenerated after the final image-affecting
  change and is bound to the exact candidate identifiers below.

Only release-candidate evidence can support a public release claim. Human
review and external-platform results must be recorded separately from
automated jobs.

## Required record schema

Create one section per candidate. Every field is required; use `not applicable`
with a reviewed rationale instead of deleting a field.

### Candidate identity

| Field | Required value |
| --- | --- |
| Status | Proposed, failed, withdrawn, superseded, or released; never infer status from a tag. |
| Evidence level | Development, integration, or release-candidate. |
| Candidate/release identifier | Proposed identifier or immutable release tag. |
| Git commit | Full 40-character commit SHA and protected-main ancestry result. |
| Image index digest | Complete OCI index digest. |
| Architecture digests | Exact AMD64 and ARM64 manifest digests. |
| Artifact-lock digest | SHA-256 of the reviewed lock set and its schema version. |
| Configuration profile | Name and digest of every qualifying configuration/fixture. |
| Created and reviewed | UTC timestamps and reviewer identities. |
| Support period | Start, supersession date when known, and end-of-support date. |

### Build and supplier inputs

Record the PostgreSQL version, PGDG RPM NEVRAs, source RPMs, byte sizes,
SHA-256 values, signing fingerprints, artifact-source identifiers, and release
note/security-advisory review. Record the exact UBI Minimal and Micro references
and manifest digests, complete runtime RPM closure, Red Hat errata review, and
architecture. Link the schema-validated locks and verified acquisition result.

Record every build, SBOM, scanner, signing, attestation, and SCAP tool version,
container image digest, rules/content digest, vulnerability database version
and timestamp, policy version, GitHub Actions workflow commit, and runner image.
`latest`, an unpinned action, or an unrecorded database cannot qualify a
candidate.

### Runtime and platform environment

For each claimed combination, record:

- architecture, host distribution/release, kernel, CPU, and time source;
- Podman/Docker client and server, OCI runtime, rootless mapping, cgroup
  version, seccomp profile, SELinux/AppArmor mode, and filesystem/storage type;
- OpenShift release, node/RHCOS release, SCC, namespace policy, CSI driver, and
  effective UID/GID when applicable;
- connected or controlled-network mode, registry/mirror digest mapping, trust
  anchors, and vulnerability-data age; and
- TLS library/provider versions, protocol/profile, certificate/trust fixture
  identifiers, and whether client certificates are in or out of scope.

Do not record private hostnames, credentials, private keys, database contents,
or sensitive environment details.

### Test and assessment results

Use one row per gate or platform result.

| Field | Required value |
| --- | --- |
| Gate | Stable test, control, or review identifier. |
| Scope | Digest, architecture, profile, platform, and relevant input versions. |
| Method | Automated test, examine, interview, manual procedure, or external-platform exercise. |
| Result | Pass, fail, not applicable, blocked, or accepted risk. |
| Evidence | Durable URL, release asset, signed attestation, or repository path plus content digest. |
| Tool/input metadata | Exact tool and database/content versions and timestamps. |
| Limitations | What the result does not establish. |
| Owner and reviewer | Accountable owner plus independent reviewer when required. |
| Executed/reviewed | UTC dates. |
| Valid until | Expiry or invalidation trigger. |

At minimum, results cover hermetic acquisition/assembly and negative cases;
native AMD64/ARM64 runtime behavior; non-root and arbitrary-UID operation;
authentication and secret handling; storage, crash recovery, backup/restore,
and minor update; TLS; logging and probes; complete SBOM/license review; Trivy
and Grype triage; provenance/signature/attestation verification; rootless RHEL
Podman; Docker compatibility; controlled-network operation; selected OpenShift
status; tailored SCAP; repository settings; and documentation rehearsal.

### Findings, exceptions, and residual risk

Record every fixed and unfixed finding, scanner disagreement, failed or
not-applicable control, unsupported claim, and accepted residual risk. Each
entry includes exact digest and architecture, advisory/control/threat ID,
component, vendor status, exposure and reachability, decision, rationale,
compensating control, owner, approver, decision date, expiry, and rescan or
reassessment trigger.

An empty findings section must state who reviewed the complete outputs and
where they are retained. A zero exit code or empty SARIF file is not a human
triage record.

### Approval and publication

Record:

- security and release reviewers and their decision;
- required checks and protected-main/ruleset verification;
- failed-candidate or prior-digest disposition;
- public GHCR index digest and immutable tags;
- Cosign issuer/identity/digest verification and bundle location;
- SBOM, provenance, attestation, scan, lock, source, license, and support links;
- published limitations, accepted risks, rollback path, security contact, and
  incident/release contacts; and
- post-publication verification on native AMD64 and ARM64.

The image index, architecture manifests, GitHub Release, support statement,
SBOM, provenance, signatures, attestations, and this ledger must identify the
same approved commit and artifact.

## Invalidation and retention

Every record lists its invalidation triggers. At minimum, changing PostgreSQL
or UBI inputs, the RPM closure, image contents, entrypoint/runtime behavior,
authentication, storage or TLS defaults, release workflow, scanner database,
SCAP content/tailoring, qualification procedure, or claimed platform
invalidates the affected candidate evidence.

Historical evidence remains labeled and available for comparison but cannot be
silently reused. Retain release evidence according to
[the maintenance policy](MAINTENANCE.md#evidence-retention); durable release
evidence must not depend only on expiring workflow artifacts.
