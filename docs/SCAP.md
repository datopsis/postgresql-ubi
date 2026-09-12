# SCAP discovery boundary

The `SCAP discovery` workflow runs on native amd64 and arm64 GitHub runners. It
uses Ubuntu's exact OpenSCAP `1.3.9+dfsg-1.1ubuntu2` packages and the
checksum-pinned ComplianceAsCode 0.1.81 prebuilt RHEL 9 data stream.

The workflow builds from the repository's locked bundle, creates a container
without starting it, verifies state `created`, exports it, and extracts the tar
with numeric owners preserved. `oscap-chroot` examines that filesystem. It does
not start PostgreSQL or execute a binary from the target image.

## Evidence boundary and selected rules

The boundary is only files present in the immutable image export: their path,
numeric user/group, and permission bits. The tailoring selects five rules for
unowned users/groups, world-writable files, setuid, and setgid. The exact
decisions and grouped exclusions are in `compliance/scap/rule-decisions.csv`.
The XML profile intentionally does not extend the RHEL 9 STIG profile.

Host kernel, boot, partitions, services, PAM/SSH, firewall, DNS, time, audit,
SIEM, runtime namespace, mounted data/configuration/secrets, active crypto
provider, PostgreSQL settings, backup, and orchestration evidence are outside
this scan. Rules needing those facts are not treated as passes; they are
not-applicable to this evidence boundary, deployment-owned, or research
required.

## Result policy

- OpenSCAP exit `0` or finding exit `2` produces evidence and permits the job
  to continue. Findings are report-only pending false-positive and security
  review.
- Download, checksum, install/version, export/ownership, parser, content,
  scanner execution, or missing-report errors fail the job.
- A reviewer triages each `fail`, `notapplicable`, `notchecked`, `unknown`, and
  `error` by architecture. `notapplicable` is not silently converted to pass.
- No remediation is applied by the scanner.
- Enabling a blocking finding policy requires an independently reviewed rule
  set, false-positive/exception process, repeatable evidence on both
  architectures, and an explicit roadmap/branch-protection change.

The reports are not evidence that a host, runtime, deployment, database, or
organization satisfies the RHEL 9 STIG or any authorization baseline. The
project makes no DISA approval, STIG certification, or compliance claim.
