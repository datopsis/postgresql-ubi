# syntax=docker/dockerfile:1.7

ARG UBI_MINIMAL_IMAGE="registry.access.redhat.com/ubi9/ubi-minimal:9.8@sha256:7fbeae18dc9476399f565e68255f602a3374ea8614ba3d14843565131a13ff93"
ARG UBI_MICRO_IMAGE="registry.access.redhat.com/ubi9/ubi-micro:9.8@sha256:f332c99eb8f798a8486821c91937f10ad64ee83d7e739303be2df051040918f6"

FROM ${UBI_MINIMAL_IMAGE} AS builder

ARG PGDG_REPO_RPM="https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm"
ARG POSTGRESQL_RPM_VERSION="18.6-1PGDG.rhel9.8"

# This development build resolves an exact PostgreSQL RPM version and its
# dependency closure during the builder stage. The first release must replace
# this with the locked, externally verified, network-disabled assembly defined
# in docs/ROADMAP.md.
# hadolint ignore=DL3041
RUN microdnf install -y dnf \
    && dnf install -y "${PGDG_REPO_RPM}" \
    && mkdir -p /runtime \
    && dnf install -y \
        --installroot=/runtime \
        --releasever=9 \
        --disablerepo=pgdg-common,pgdg17,pgdg16,pgdg15,pgdg14 \
        --setopt=install_weak_deps=0 \
        --setopt=keepcache=0 \
        "postgresql18-${POSTGRESQL_RPM_VERSION}" \
        "postgresql18-libs-${POSTGRESQL_RPM_VERSION}" \
        "postgresql18-server-${POSTGRESQL_RPM_VERSION}" \
        ca-certificates nss_wrapper tzdata \
    && dnf clean all \
    && microdnf clean all \
    && rm -rf \
        /runtime/run/* \
        /runtime/tmp/* \
        /runtime/var/cache/dnf \
        /runtime/var/log/* \
        /runtime/var/tmp/* \
    && mkdir -p /runtime/var/lib/pgsql /runtime/run/postgresql \
    && chown -R 26:0 /runtime/var/lib/pgsql /runtime/run/postgresql \
    && chmod 2775 /runtime/var/lib/pgsql /runtime/run/postgresql

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
  CMD ["/usr/pgsql-18/bin/pg_isready", "--quiet", "--host=/run/postgresql", "--port=5432"]

STOPSIGNAL SIGINT

ENTRYPOINT ["postgresql-entrypoint"]
CMD ["postgres"]
