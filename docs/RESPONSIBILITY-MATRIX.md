# Deployment responsibility matrix

The image cannot implement the following system controls. A deployment is not
supported merely because it starts; owners must select, document, test, monitor,
and periodically reassess these controls.

| Area | Deployment requirement | Evidence owner |
| --- | --- | --- |
| Network/firewall/ingress | Default-deny reachability; expose 5432 only to approved clients; control egress, admin paths and segmentation; test unauthorized paths. | Network/platform owner |
| DNS and time | Authenticated/controlled name resolution as required; trusted synchronized time for certificates, logs, recovery and evidence. | Platform infrastructure |
| Secrets | File-mounted least-privilege secrets; generation, access audit, rotation, revocation and deletion; never environment/argv/image. | Secret/database owner |
| SELinux | Enforcing supported policy and correct volume labels; review denials; never disable enforcement as a routine fix. | RHEL/platform owner |
| Seccomp and capabilities | Runtime default/reviewed seccomp, drop all capabilities, no-new-privileges, no privilege/host namespaces/devices. | Runtime/platform owner |
| Monitoring and SIEM | Health/availability/security events, authenticated collection, access controls, capacity/rate alerts, interruption detection and correlation. | Operations/security monitoring |
| Logs | Event policy, minimization/redaction, trusted timestamps, integrity, restricted retention, search/export and verified disposal. | SIEM/privacy/records owners |
| Backups | Consistent method, encryption, key separation, restricted custody, immutability where needed, retention/disposal, isolated restore tests and RPO/RTO. | Database/storage/recovery owners |
| Storage | Dedicated durable volume, ownership/labels, encryption/access, capacity and latency alerts, snapshot semantics, sanitization. | Storage/platform owner |
| Resources | CPU/memory/PID/connection/disk/WAL/log quotas, bounded `/dev/shm` and `/tmp`, restart throttling and workload capacity tests. | Platform/database owner |
| Controlled transfer | Verify public digest/signature/evidence before transfer; record internal digest mapping, chain of custody, internal CA/time, advisory/feed age and rollback. | Registry/network security |
| Decommissioning | Stop clients, revoke all credentials/certificates, remove workload, sanitize volumes, expire/sanitize backups and logs, remove DNS/network rules, retain required incident/release evidence. | System/data owner |

The organization must also assign application, database, host, PKI, network,
storage, backup, SIEM, vulnerability-acceptance, incident, privacy/legal, and
authorization owners. Separation of duties and approval thresholds are local
governance decisions; this project does not invent them.
