#!/bin/sh
set -eu

postgres_major=18

fatal() {
    printf 'postgresql-entrypoint: %s\n' "$*" >&2
    exit 1
}

configure_arbitrary_uid() {
    if id -un >/dev/null 2>&1; then
        return
    fi

    wrapper=/usr/lib64/libnss_wrapper.so
    test -r "${wrapper}" || fatal "current UID is unknown and nss_wrapper is unavailable"

    passwd_file=/tmp/postgresql-passwd
    cp /etc/passwd "${passwd_file}"
    printf 'postgres:x:%s:0:PostgreSQL Server:%s:/sbin/nologin\n' \
        "$(id -u)" "${PGDATA}" >>"${passwd_file}"
    export NSS_WRAPPER_PASSWD="${passwd_file}"
    export NSS_WRAPPER_GROUP=/etc/group
    export LD_PRELOAD="${wrapper}${LD_PRELOAD:+:${LD_PRELOAD}}"
}

read_initial_password() {
    if test -n "${POSTGRES_PASSWORD:-}" && test -n "${POSTGRES_PASSWORD_FILE:-}"; then
        fatal "set only one of POSTGRES_PASSWORD or POSTGRES_PASSWORD_FILE"
    fi

    if test -n "${POSTGRES_PASSWORD_FILE:-}"; then
        test -r "${POSTGRES_PASSWORD_FILE}" || \
            fatal "POSTGRES_PASSWORD_FILE is not readable"
        POSTGRES_PASSWORD=$(cat "${POSTGRES_PASSWORD_FILE}")
    fi

    test -n "${POSTGRES_PASSWORD:-}" || \
        fatal "initialization requires POSTGRES_PASSWORD or POSTGRES_PASSWORD_FILE"
}

initialize_database() {
    read_initial_password
    umask 077
    password_file="/tmp/postgresql-password.$$"
    printf '%s' "${POSTGRES_PASSWORD}" >"${password_file}"
    trap 'rm -f "${password_file}"' EXIT HUP INT TERM

    initdb \
        --pgdata="${PGDATA}" \
        --username="${POSTGRES_USER}" \
        --pwfile="${password_file}" \
        --auth-host=scram-sha-256 \
        --auth-local=trust \
        --encoding=UTF8

    printf "\nlisten_addresses = '*'\nunix_socket_directories = '/tmp'\npassword_encryption = 'scram-sha-256'\n" \
        >>"${PGDATA}/postgresql.conf"
    printf '\nhost all all all scram-sha-256\n' >>"${PGDATA}/pg_hba.conf"

    pg_ctl --pgdata="${PGDATA}" \
        --options="-c listen_addresses='' -c unix_socket_directories=/tmp" \
        --wait start

    database=${POSTGRES_DB:-${POSTGRES_USER}}
    if test "${database}" != "${POSTGRES_USER}"; then
        createdb --host=/tmp --username="${POSTGRES_USER}" -- "${database}"
    fi

    pg_ctl --pgdata="${PGDATA}" --mode=fast --wait stop
    rm -f "${password_file}"
    trap - EXIT HUP INT TERM
    unset POSTGRES_PASSWORD
}

if test "${1:-}" = "postgres"; then
    configure_arbitrary_uid
    mkdir -p "${PGDATA}"
    test -w "${PGDATA}" || fatal "PGDATA is not writable: ${PGDATA}"

    if test ! -s "${PGDATA}/PG_VERSION"; then
        if test -n "$(find "${PGDATA}" -mindepth 1 -maxdepth 1 -print -quit)"; then
            fatal "PGDATA is non-empty but has no PG_VERSION file"
        fi
        initialize_database
    else
        installed_major=$(cat "${PGDATA}/PG_VERSION")
        test "${installed_major}" = "${postgres_major}" || \
            fatal "PGDATA major ${installed_major} is incompatible with PostgreSQL ${postgres_major}"
    fi
fi

exec "$@"
