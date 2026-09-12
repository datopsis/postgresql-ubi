# Incident response responsibilities

The deploying organization commands incidents involving its system and data.
Datopsis commands repository, build, signing, and published-image incidents and
coordinates with PostgreSQL, PGDG, Red Hat, GitHub, and registry providers.

## Response sequence

1. **Declare and preserve.** Assign incident commander, recorder, scope and
   time source. Preserve image digest, manifest, host/runtime versions,
   configuration hashes, access/audit logs, storage snapshots, release bundles,
   workflow runs, and relevant volatile state under legal/privacy rules. Never
   put database contents, credentials, private keys, personal data, or internal
   topology in a public issue.
2. **Contain.** Restrict ingress/egress, revoke sessions, isolate affected
   workloads and runners, disable compromised workflows/credentials, and
   quarantine affected registry digests. Do not move/reuse a tag or destroy the
   only evidence. Weigh immediate shutdown against evidence and availability.
3. **Rotate trust.** Rotate database/application credentials, bootstrap and
   backup secrets, TLS keys/certificates, CA trust where required, registry and
   GitHub credentials, signing authority, and mirror credentials. Reissuing a
   certificate without revocation/consumer trust updates is incomplete.
4. **Eradicate and recover.** Determine root cause; rebuild from reviewed locked
   inputs on clean infrastructure; restore only from verified, isolated,
   tested recovery points; qualify and sign a new digest. PostgreSQL data
   downgrade is not assumed safe.
5. **Notify and withdraw.** Coordinate embargoes and vendor reports. Identify
   affected digests/architectures, exposure, mitigation, replacement, evidence
   confidence, and rollback/restore limits. Mark releases withdrawn and decide
   registry quarantine/removal while preserving restricted evidence.
6. **Learn.** Within the organization's target period, record timeline, root
   and contributing causes, control failures, data/evidence impact, detection
   gaps, corrective owners/dates, and needed threat/control updates. Rehearse
   corrections before closure.

## Decision ownership

| Decision | Accountable party |
| --- | --- |
| Customer workload isolation, data impact, legal/regulatory notification | Deploying organization incident/legal/privacy owners |
| Database credential, TLS certificate, backup key, and application-secret rotation | Database, PKI, backup, and application owners |
| Host/runtime isolation, forensic capture, network controls | Platform/security operations |
| Repository/workflow lockdown, upstream coordination, image withdrawal and replacement | Datopsis maintainer |
| Registry quarantine and consumer notice delivery | Datopsis plus registry/communications owner |
| Backup selection, integrity, restore point and return to service | Organization recovery authority |

Tabletop this sequence before first release and annually, and perform a focused
rehearsal after material trust-boundary changes. A drill uses synthetic facts
and no production secrets or real vulnerability report.
