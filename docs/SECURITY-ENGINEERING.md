# Security engineering record

This package describes component capabilities and shared responsibilities. It is
not a completed Security Controls Traceability Matrix (SCTM), System Security
Plan (SSP), authorization, assessor decision, STIG certification, or claim that
an operating deployment is compliant.

## Authoritative sources and scope

`compliance/source-register.json` is the machine-readable source register. Its
hashes were calculated from the exact retrieved payloads on 2026-09-12. The
source documents are referenced rather than copied so upstream license,
distribution, and update status stay visible. A quarterly review, every
PostgreSQL minor update, and any assurance-tool update must recheck publication
status and hashes.

The analysis used NIST SP 800-53 Rev. 5 and SP 800-53A Rev. 5 Release 5.2.0;
DISA Database SRG V4R5, Container Platform SRG V2R4, and RHEL 9 STIG V2R9;
PostgreSQL 18 documentation; OSCAL 1.2.3; and ComplianceAsCode 0.1.81. The
active Crunchy Data Postgres 16 STIG V1R3 was reviewed only for concepts. Its
paths, packaging, extensions, scripts, roles, and version are not this PGDG
PostgreSQL 18 component. The PostgreSQL 9.x STIG is sunset. Neither product
guide supplies executable instructions or evidence for this image.

This is a risk-based component subset, not an assertion that every control in
the source catalogs applies to an OCI image. The selected NIST controls cover
authorization, logging, baseline configuration, recovery, authenticators,
incident response, transport, cryptography, flaw remediation, and supply-chain
integrity. The DISA review separated requirements into:

- image filesystem and supply-chain requirements the repository can own;
- database mechanisms the image can support but a deployment must configure;
- host, container-platform, network, identity, monitoring, backup, and incident
  requirements inherited from operators; and
- product-specific or cryptographic claims that remain unsupported or require
  research.

The concrete cross-source sample reviewed for the initial component boundary is
listed below. Broad source catalogs are not silently marked satisfied; only
these requirements were classified as component records, while the SCAP rule
decision file records the RHEL rule boundary.

| Source requirement | OSCAL record | Classification and disposition |
| --- | --- | --- |
| NIST AC-3; `SRG-APP-000033-DB-000084` | AC-3 | Deployment-supported authorization mechanisms. |
| NIST AU-2; `SRG-APP-000091-DB-000066` | AU-2 | Deployment-supported logging; SIEM is inherited. |
| NIST CM-2; `SRG-APP-000516-CTR-001325` | CM-2 | Image-owned immutable component baseline. |
| NIST CP-9 | CP-9 | Inherited backup policy and execution. |
| NIST IA-5; `SRG-APP-000171-DB-000074` | IA-5 | Deployment-supported SCRAM/bootstrap behavior. |
| NIST IR-4 | IR-4 | Inherited system response with maintainer withdrawal support. |
| NIST SC-8; `SRG-APP-000441-DB-000378` | SC-8 | Deployment-supported TLS; network/client enforcement is external. |
| NIST SC-13; `SRG-APP-000179-DB-000114` | SC-13 | Research required; no validated-module claim. |
| NIST SI-2; `SRG-APP-000456-DB-000390` | SI-2 | Image-owned monitoring/rebuild/withdrawal process. |
| NIST SR-4 | SR-4 | Image-owned publisher, source, provenance, and signing verification. |

The active Crunchy Data Postgres 16 STIG is classified `not-applicable` as
executable product guidance for PGDG PostgreSQL 18. Its security concepts are
cross-check inputs only. The sunset PostgreSQL 9.x STIG is `not-applicable` and
superseded for this version. A future active PGDG PostgreSQL 18 guide would be
`research-required` until every packaging and command assumption is tested.

`compliance/oscal/component-definition.json` is canonical. Every analyzed
control has exactly one ownership classification and records rationale,
residual risk, evidence, owner, review state, all three SP 800-53A assessment
method types where appropriate, default/configurable state, prerequisites,
restart behavior, operational impact, loss of protection, and limitations.
Run `python scripts/cybersecurity.py` to regenerate the SCTM-importable CSV and
human view, or add `--check` to detect drift.

## Review and decision rules

All initial entries are `pending-independent-review`. Before first release, a
reviewer who did not author the decision must examine adopted, excluded,
unsupported, research-required, and not-applicable classifications. The review
record must identify the commit, reviewer, date, sources, disagreements,
decision, and follow-up issue. The accountable maintainer cannot self-approve
this independence requirement.

A reviewer must reject an entry if its evidence does not demonstrate the
described component behavior, if a deployment responsibility is represented as
image-owned, or if the limitation/residual risk is missing. Any material input,
behavior, architecture, tool, rule selection, or source update invalidates the
affected review.

## Artifact integrity and schema validation

CI downloads the official NIST OSCAL Component Definition schema 1.2.3,
verifies SHA-256
`95e76881151ececd5cb1a93ff0f70ad74b8cc1aa58771626ac8b262bf2c8e001`,
then validates the component definition with hash-locked Python dependencies.
Repository tests independently enforce complete properties, one
classification per control, evidence paths, source-register format, generated
view freshness, and vulnerability-exception constraints.

## Evidence lifecycle

Evidence identifies a commit or immutable image digest, architecture, test/tool
version, input hashes, time, result, and retained artifact. A new image digest,
package closure, PostgreSQL behavior, base image, control source, scanner,
content version, database, configuration profile, or assessment method makes
the affected evidence stale. Stale evidence is retained for history but cannot
qualify a newer candidate.

The trace is:

`source-register.json` → OSCAL control and classification → repository behavior
or external owner → assessment method → evidence path → limitation and residual
risk → independent review record.

## Known open decisions

- No independent Package 5 review has yet been recorded.
- SCAP is report-only discovery and cannot qualify a host or deployment.
- No applicable FIPS/CMVP boundary has been established.
- No product-specific PostgreSQL 18 STIG exists for this PGDG image.
- Package 6 must qualify exact platforms and external control implementations.
