# syntax=docker/dockerfile:1.7

ARG UBI_MINIMAL_IMAGE="registry.access.redhat.com/ubi9/ubi-minimal:9.8@sha256:7fbeae18dc9476399f565e68255f602a3374ea8614ba3d14843565131a13ff93"
ARG UBI_MICRO_IMAGE="registry.access.redhat.com/ubi9/ubi-micro:9.8@sha256:f332c99eb8f798a8486821c91937f10ad64ee83d7e739303be2df051040918f6"

FROM scratch AS pgdg-artifacts-amd64

ADD --checksum=sha256:ae57ba32d87fa3c311da9545bc85682ae04dc41cfbabf60d7f6c185099604f8a \
    https://download.postgresql.org/pub/repos/yum/18/redhat/rhel-9-x86_64/postgresql18-18.6-1PGDG.rhel9.8.x86_64.rpm /postgresql18.rpm
ADD --checksum=sha256:7a4d55c02b8bab1b359aa25ce53d81db77cd39026a980dd8f0210031a5c31654 \
    https://download.postgresql.org/pub/repos/yum/18/redhat/rhel-9-x86_64/postgresql18-libs-18.6-1PGDG.rhel9.8.x86_64.rpm /postgresql18-libs.rpm
ADD --checksum=sha256:f7f1915d63756f6a37f3f2e5cc84d03893d0d7a55dab8ac350871bd1c48a0754 \
    https://download.postgresql.org/pub/repos/yum/18/redhat/rhel-9-x86_64/postgresql18-server-18.6-1PGDG.rhel9.8.x86_64.rpm /postgresql18-server.rpm

FROM scratch AS pgdg-artifacts-arm64

ADD --checksum=sha256:3ec399a4d57b43cbba03f610adc4a4c6daaea0dc8b4f3d73175b1dedf7e2bddf \
    https://download.postgresql.org/pub/repos/yum/18/redhat/rhel-9-aarch64/postgresql18-18.6-1PGDG.rhel9.8.aarch64.rpm /postgresql18.rpm
ADD --checksum=sha256:662bac810d50ece9d32f7ab6960f01e8e1416cc0a0634a4ea7f7ec8ea744146b \
    https://download.postgresql.org/pub/repos/yum/18/redhat/rhel-9-aarch64/postgresql18-libs-18.6-1PGDG.rhel9.8.aarch64.rpm /postgresql18-libs.rpm
ADD --checksum=sha256:761001b6e560041f2f6f0d7abe9e57b30a98a2c039b81682d77969928a366add \
    https://download.postgresql.org/pub/repos/yum/18/redhat/rhel-9-aarch64/postgresql18-server-18.6-1PGDG.rhel9.8.aarch64.rpm /postgresql18-server.rpm

ARG TARGETARCH
# The selected scratch stage contains checksum-pinned artifacts only.
# hadolint ignore=DL3006
FROM pgdg-artifacts-${TARGETARCH} AS pgdg-artifacts

FROM scratch AS pgdg-key

ADD --checksum=sha256:a70c9527426017d00fa4e6f9d2941d515357a27a7be82e155248ece53bbe5453 \
    https://download.postgresql.org/pub/repos/yum/keys/PGDG-RPM-GPG-KEY-RHEL /PGDG-RPM-GPG-KEY-RHEL
ADD --checksum=sha256:cc506fa92aa97e8e58f88551a2ec99a61d9d603f7f2c1ae0c06191f58c29979f \
    https://download.postgresql.org/pub/repos/yum/keys/PGDG-RPM-GPG-KEY-AARCH64-RHEL /PGDG-RPM-GPG-KEY-AARCH64-RHEL

FROM ${UBI_MINIMAL_IMAGE} AS builder

COPY --from=pgdg-artifacts / /tmp/pgdg/
COPY --from=pgdg-key /PGDG-RPM-GPG-KEY-RHEL /PGDG-RPM-GPG-KEY-AARCH64-RHEL /tmp/pgdg/

# PostgreSQL artifacts and their signing key are checksum-pinned above. RPM
# signatures are then verified before DNF resolves only their UBI dependencies.
# The first release must also lock that dependency closure and assemble without
# network access as defined in docs/ROADMAP.md.
# hadolint ignore=DL3041
RUN microdnf install -y dnf \
    && rpm --import \
        /tmp/pgdg/PGDG-RPM-GPG-KEY-RHEL \
        /tmp/pgdg/PGDG-RPM-GPG-KEY-AARCH64-RHEL \
    && rpm --checksig /tmp/pgdg/*.rpm \
    && mkdir -p /runtime \
    && rpm --root /runtime --initdb \
    && rpm --root /runtime --import \
        /tmp/pgdg/PGDG-RPM-GPG-KEY-RHEL \
        /tmp/pgdg/PGDG-RPM-GPG-KEY-AARCH64-RHEL \
    && dnf install -y \
        --installroot=/runtime \
        --releasever=9 \
        --setopt=localpkg_gpgcheck=1 \
        --setopt=install_weak_deps=0 \
        --setopt=keepcache=0 \
        /tmp/pgdg/postgresql18.rpm \
        /tmp/pgdg/postgresql18-libs.rpm \
        /tmp/pgdg/postgresql18-server.rpm \
        ca-certificates nss_wrapper tzdata \
    && dnf clean all \
    && microdnf clean all \
    && rm -rf \
        /runtime/run/* \
        /runtime/tmp/* \
        /runtime/var/cache/dnf \
        /runtime/var/log/* \
        /runtime/var/tmp/* \
    && mkdir -p /runtime/var/lib/pgsql \
    && chown -R 26:0 /runtime/var/lib/pgsql \
    && chmod 2775 /runtime/var/lib/pgsql

FROM ${UBI_MICRO_IMAGE}

ARG POSTGRESQL_VERSION="18.6"
ARG POSTGRESQL_RPM_VERSION="18.6-1PGDG.rhel9.8"

LABEL org.opencontainers.image.title="PostgreSQL on Red Hat UBI 9" \
      org.opencontainers.image.description="A security-oriented, rootless PostgreSQL image built on Red Hat UBI 9 Micro" \
      org.opencontainers.image.source="https://github.com/datopsis/postgresql-ubi" \
      org.opencontainers.image.documentation="https://github.com/datopsis/postgresql-ubi#readme" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.vendor="Datopsis" \
      org.opencontainers.image.version="${POSTGRESQL_VERSION}" \
      io.datopsis.postgresql.rpm-version="${POSTGRESQL_RPM_VERSION}"

COPY --from=builder /runtime/ /
COPY --chown=0:0 --chmod=0755 container/entrypoint.sh /usr/local/bin/postgresql-entrypoint

ENV LANG="C.UTF-8" \
    TZ="UTC" \
    PATH="/usr/pgsql-18/bin:${PATH}" \
    PGDATA="/var/lib/pgsql/data" \
    POSTGRES_USER="postgres"

VOLUME ["/var/lib/pgsql"]

USER 26:0
WORKDIR /var/lib/pgsql

EXPOSE 5432

HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=5 \
  CMD ["/usr/pgsql-18/bin/psql", "--quiet", "--host=/tmp", "--username=postgres", "--dbname=postgres", "--command=SELECT 1"]

STOPSIGNAL SIGINT

ENTRYPOINT ["postgresql-entrypoint"]
CMD ["postgres"]
