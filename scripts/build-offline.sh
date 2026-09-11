#!/usr/bin/env bash
set -Eeuo pipefail

case "$(uname -m)" in
    x86_64) architecture=amd64 ;;
    aarch64|arm64) architecture=arm64 ;;
    *) printf 'unsupported native architecture: %s\n' "$(uname -m)" >&2; exit 1 ;;
esac

runtime=${CONTAINER_RUNTIME:-podman}
image=${IMAGE:-localhost/postgresql-ubi:test}
lock=artifacts/locks/${architecture}.json
bundle=.artifact-bundle/${architecture}

command -v "${runtime}" >/dev/null
command -v gpg >/dev/null
test -f "${lock}"
test ! -e "${bundle}"

python3 scripts/artifacts.py acquire --lock "${lock}" --output "${bundle}"
bash scripts/verify-key-fingerprints.sh "${bundle}"
lock_sha=$(sha256sum "${lock}" | cut -d' ' -f1)
builder=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["base_images"]["builder"]["reference"])' "${lock}")
runtime_base=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["base_images"]["runtime"]["reference"])' "${lock}")

"${runtime}" pull "${builder}"
"${runtime}" pull "${runtime_base}"
"${runtime}" tag "${builder}" localhost/postgresql-ubi-builder:locked
"${runtime}" tag "${runtime_base}" localhost/postgresql-ubi-runtime:locked
test "$("${runtime}" image inspect --format '{{.Architecture}}' localhost/postgresql-ubi-builder:locked)" = "${architecture}"
test "$("${runtime}" image inspect --format '{{.Architecture}}' localhost/postgresql-ubi-runtime:locked)" = "${architecture}"

if test "${runtime}" = docker; then
    pull_flag=false
else
    pull_flag=never
fi
build_arguments=(--file Containerfile --tag "${image}" --network=none \
    --pull="${pull_flag}" --no-cache \
    --build-arg UBI_MINIMAL_IMAGE=localhost/postgresql-ubi-builder:locked \
    --build-arg UBI_MICRO_IMAGE=localhost/postgresql-ubi-runtime:locked \
    --build-arg ARTIFACT_LOCK_SHA256="${lock_sha}" .)
if test "${runtime}" = docker && test -n "${BUILD_METADATA_FILE:-}"; then
    build_arguments=(--metadata-file "${BUILD_METADATA_FILE}" "${build_arguments[@]}")
fi

"${runtime}" build "${build_arguments[@]}"
