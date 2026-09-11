#!/usr/bin/env bash
set -Eeuo pipefail

architecture=${1:?usage: resolve-lock.sh ARCHITECTURE INPUT_DIR OUTPUT_DIR}
input_dir=${2:?usage: resolve-lock.sh ARCHITECTURE INPUT_DIR OUTPUT_DIR}
output_dir=${3:?usage: resolve-lock.sh ARCHITECTURE INPUT_DIR OUTPUT_DIR}

case "${architecture}" in
    amd64) rpm_architecture=x86_64 ;;
    arm64) rpm_architecture=aarch64 ;;
    *) printf 'unsupported architecture: %s\n' "${architecture}" >&2; exit 1 ;;
esac

test -d "${input_dir}/rpms"
test -d "${input_dir}/keys"
test ! -e "${output_dir}"
mkdir -p "${output_dir}/rpms" "${output_dir}/srpms"

# Resolution is deliberately online and isolated from ordinary assembly.
microdnf install -y dnf dnf-plugins-core >/dev/null
rpm --import "${input_dir}"/keys/*
rpm --checksig "${input_dir}"/rpms/*.rpm

mkdir -p /tmp/resolve-root
dnf install -y \
    --downloadonly \
    --downloaddir="${output_dir}/rpms" \
    --installroot=/tmp/resolve-root \
    --releasever=9 \
    --setopt=localpkg_gpgcheck=1 \
    --setopt=install_weak_deps=0 \
    --setopt=keepcache=0 \
    "${input_dir}"/rpms/*.rpm \
    ca-certificates nss_wrapper tzdata >/dev/null
cp "${input_dir}"/rpms/*.rpm "${output_dir}/rpms/"

query_format='%{repoid}|%{location}'
binary_inventory="${output_dir}/binary-inventory.tsv"
: >"${binary_inventory}"

find_url() {
    local spec=$1
    local mode=${2:-binary}
    local result
    if test "${mode}" = source; then
        result=$(dnf repoquery --disablerepo='*' \
            --enablerepo='ubi-9-*-source-rpms' \
            --qf "${query_format}" "${spec}")
    else
        result=$(dnf repoquery --qf "${query_format}" "${spec}")
    fi
    test "$(printf '%s\n' "${result}" | sed '/^$/d' | wc -l)" -eq 1
    printf '%s\n' "${result}"
}

while IFS= read -r rpm_path; do
    metadata=$(rpm -qp --qf \
        '%{NAME}|%{EPOCHNUM}|%{VERSION}|%{RELEASE}|%{ARCH}|%{SOURCERPM}|%{SIGPGP:pgpsig}|%{SIGGPG:pgpsig}' \
        "${rpm_path}")
    IFS='|' read -r name epoch version release package_arch source_rpm sigpgp siggpg \
        <<<"${metadata}"
    filename=$(basename "${rpm_path}")
    if [[ ${name} == postgresql18* ]]; then
        repository=pgdg-18
        url="https://download.postgresql.org/pub/repos/yum/18/redhat/rhel-9-${rpm_architecture}/${filename}"
    else
        spec="${name}-${epoch}:${version}-${release}.${package_arch}"
        query=$(find_url "${spec}")
        repository=${query%%|*}
        location=${query#*|}
        case "${repository}" in
            ubi-9-baseos-rpms) component=baseos ;;
            ubi-9-appstream-rpms) component=appstream ;;
            ubi-9-codeready-builder-rpms) component=codeready-builder ;;
            *) printf 'unexpected binary repository: %s\n' "${repository}" >&2; exit 1 ;;
        esac
        url="https://cdn-ubi.redhat.com/content/public/ubi/dist/ubi9/9/${rpm_architecture}/${component}/os/${location}"
    fi
    signature="${sigpgp} ${siggpg}"
    key_id=$(sed -n 's/.*[Kk]ey ID \([0-9A-Fa-f]*\).*/\1/p' <<<"${signature}" | head -n1)
    test -n "${key_id}"
    size=$(stat -c '%s' "${rpm_path}")
    sha256=$(sha256sum "${rpm_path}" | cut -d' ' -f1)
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "${filename}" "${name}" "${epoch}" "${version}" "${release}" \
        "${package_arch}" "${source_rpm}" "${key_id}" "${repository}" \
        "${url}" "${size}" "${sha256}" >>"${binary_inventory}"
done < <(find "${output_dir}/rpms" -maxdepth 1 -type f -name '*.rpm' | sort)

cut -f7 "${binary_inventory}" | sort -u >"${output_dir}/source-names.txt"
source_inventory="${output_dir}/source-inventory.tsv"
: >"${source_inventory}"

while IFS= read -r source_rpm; do
    if [[ ${source_rpm} == postgresql18-* ]]; then
        repository=pgdg-18-source
        url="https://dnf-srpms.postgresql.org/srpms/18/redhat/rhel-9-x86_64/${source_rpm}"
    else
        spec=${source_rpm%.rpm}
        query=$(find_url "${spec}" source)
        repository=${query%%|*}
        location=${query#*|}
        case "${repository}" in
            ubi-9-baseos-source-rpms) component=baseos ;;
            ubi-9-appstream-source-rpms) component=appstream ;;
            ubi-9-codeready-builder-source-rpms) component=codeready-builder ;;
            *) printf 'unexpected source repository: %s\n' "${repository}" >&2; exit 1 ;;
        esac
        url="https://cdn-ubi.redhat.com/content/public/ubi/dist/ubi9/9/${rpm_architecture}/${component}/source/SRPMS/${location}"
    fi
    curl --fail --location --proto '=https' --retry 3 \
        --output "${output_dir}/srpms/${source_rpm}" "${url}"
    rpm --checksig "${output_dir}/srpms/${source_rpm}"
    size=$(stat -c '%s' "${output_dir}/srpms/${source_rpm}")
    sha256=$(sha256sum "${output_dir}/srpms/${source_rpm}" | cut -d' ' -f1)
    printf '%s\t%s\t%s\t%s\t%s\n' \
        "${source_rpm}" "${repository}" "${url}" "${size}" "${sha256}" \
        >>"${source_inventory}"
done <"${output_dir}/source-names.txt"

sort -o "${binary_inventory}" "${binary_inventory}"
sort -o "${source_inventory}" "${source_inventory}"
