#!/usr/bin/env bash
set -Eeuo pipefail
architecture=${ARCHITECTURE:?native architecture required}
case "${architecture}" in amd64|arm64) ;; *) exit 1 ;; esac
lock="artifacts/locks/${architecture}.json"
python3 scripts/artifacts.py validate-lock "${lock}"
builder=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["base_images"]["builder"]["reference"])' "${lock}")
output="vulnerability-gate-${architecture}"
mkdir "${output}"
container="ubi-vulnerability-query-${architecture}-${RANDOM}-${RANDOM}"
trap 'docker rm --force "${container}" >/dev/null 2>&1 || true' EXIT
# The query has an overall deadline as well as DNF network timeouts. Preserve the
# original .repo files/config before installing tooling, just like the resolver.
status=0
timeout --signal=TERM --kill-after=10s 300s docker run --rm --interactive --name "${container}" \
    --platform "linux/${architecture}" \
    --volume "${PWD}:/work:ro" --volume "${PWD}/${output}:/evidence" \
    --workdir /work --env "ARCHITECTURE=${architecture}" \
    --env PYTHONDONTWRITEBYTECODE=1 "${builder}" bash -eu -s <<'QUERY' || status=$?
        cp -a /etc/yum.repos.d /tmp/ubi-repos
        cp /etc/dnf/dnf.conf /tmp/ubi-dnf.conf
        microdnf --setopt=*.skip_if_unavailable=0 install -y dnf dnf-plugins-core
        python3 -m unittest discover -s tests -p rpm_versions.py -v
        python3 scripts/vulnerability_gate.py \
            --lock "artifacts/locks/${ARCHITECTURE}.json" \
            --trivy "trivy-all-${ARCHITECTURE}.json" \
            --grype "grype-all-${ARCHITECTURE}.json" \
            --output /evidence/gate.json
QUERY
# Bootstrap, timeout, scanner, or query failures still produce visible evidence.
if test ! -s "${output}/gate.json"; then
    python3 scripts/vulnerability_gate.py \
        --lock "${lock}" --trivy "trivy-all-${architecture}.json" \
        --grype "grype-all-${architecture}.json" --output "${output}/gate.json" \
        --query-error "native query did not produce a report (exit ${status})" || status=1
fi
if test -n "${GITHUB_STEP_SUMMARY:-}"; then
    cat "${output}/gate.md" >> "${GITHUB_STEP_SUMMARY}"
fi
exit "${status}"
