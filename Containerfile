# syntax=docker/dockerfile:1.7

ARG UBI_MINIMAL_IMAGE="registry.access.redhat.com/ubi9/ubi-minimal:9.8@sha256:7fbeae18dc9476399f565e68255f602a3374ea8614ba3d14843565131a13ff93"
ARG UBI_MICRO_IMAGE="registry.access.redhat.com/ubi9/ubi-micro:9.8@sha256:f332c99eb8f798a8486821c91937f10ad64ee83d7e739303be2df051040918f6"

FROM ${UBI_MICRO_IMAGE} AS runtime-base

FROM ${UBI_MINIMAL_IMAGE} AS builder

ARG TARGETARCH
ARG ARTIFACT_LOCK_SHA256
COPY .artifact-bundle/${TARGETARCH}/ /tmp/artifacts/
COPY --chmod=0755 scripts/verify-rpm-bundle.sh /usr/local/bin/verify-rpm-bundle
COPY --from=runtime-base / /final/
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# The bundle is acquired and hash/fingerprint verified before this build. The
# build rechecks its selected lock, exact RPM metadata, and signatures without
# contacting repositories or resolving dependencies.
RUN test -n "${ARTIFACT_LOCK_SHA256}" \
    && test "$(cat /tmp/artifacts/LOCK-SHA256)" = "${ARTIFACT_LOCK_SHA256}" \
    && verify-rpm-bundle /tmp/artifacts \
    && mkdir -p /runtime \
    && rpm --root /runtime --initdb \
    && rpm --root /runtime --import /tmp/artifacts/keys/* \
    && rpm --root /runtime --install /tmp/artifacts/rpms/*.rpm \
    && rpm --root /runtime --query --all \
        --qf '%{NAME}-%{VERSION}-%{RELEASE}\n' \
        | sed -n '/^gpg-pubkey-/p' > /tmp/imported-keys \
    && while IFS= read -r key; do \
        rpm --root /runtime --erase "${key}"; \
    done < /tmp/imported-keys \
    && cp -a /runtime/. /final/ \
    && rm -rf \
        /final/etc/dnf \
        /final/etc/pki/entitlement \
        /final/etc/pki/rpm-gpg \
        /final/etc/rhsm \
        /final/etc/yum.repos.d \
        /final/run/* \
        /final/tmp/* \
        /final/var/cache/dnf \
        /final/var/cache/yum \
        /final/var/lib/rhsm \
        /final/var/log/* \
        /final/var/tmp/* \
    && find /final -xdev -type f -perm /6000 -exec chmod a-s {} + \
    && ! find /final -xdev -type f -perm -0002 -print -quit | grep -q . \
    && mkdir -p /final/var/lib/pgsql \
    && chown -R 26:0 /final/var/lib/pgsql \
    && chmod 2775 /final/var/lib/pgsql

FROM scratch

ARG POSTGRESQL_VERSION="18.6"
ARG POSTGRESQL_RPM_VERSION="18.6-1PGDG.rhel9.8"
ARG ARTIFACT_LOCK_SHA256

LABEL org.opencontainers.image.title="PostgreSQL on Red Hat UBI 9" \
      org.opencontainers.image.description="A security-oriented, rootless PostgreSQL image built on Red Hat UBI 9 Micro" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.vendor="Datopsis" \
      org.opencontainers.image.version="${POSTGRESQL_VERSION}" \
      io.datopsis.postgresql.rpm-version="${POSTGRESQL_RPM_VERSION}" \
      io.datopsis.artifact-lock.sha256="${ARTIFACT_LOCK_SHA256}"

COPY --from=builder /final/ /
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
