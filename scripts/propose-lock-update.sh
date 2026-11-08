#!/usr/bin/env bash
set -Eeuo pipefail

python scripts/artifacts.py validate-inputs artifacts/lock-inputs.json
python scripts/artifacts.py validate-lock artifacts/locks/amd64.json
python scripts/artifacts.py validate-lock artifacts/locks/arm64.json
python - <<'PY'
import json
from pathlib import Path

inputs = json.loads(Path('artifacts/lock-inputs.json').read_text())
for arch in ('amd64', 'arm64'):
    lock = json.loads(Path(f'artifacts/locks/{arch}.json').read_text())
    assert {role: base['reference'] for role, base in lock['base_images'].items()} == inputs['base_images']
    assert lock['architecture'] == arch
PY

if git diff --quiet -- Containerfile artifacts/lock-inputs.json artifacts/locks; then
    echo 'No base or package changes; no PR needed.'
    exit 0
fi

# A new branch preserves previous review evidence and avoids rewriting or
# overwriting a maintainer's edits to an older proposal.
branch="automation/artifact-locks-${GITHUB_RUN_ID:?}-${GITHUB_RUN_ATTEMPT:?}"
git switch -c "${branch}"
git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add Containerfile artifacts/lock-inputs.json artifacts/locks/amd64.json artifacts/locks/arm64.json
git commit -m 'fix(deps): refresh UBI bases and artifact locks'
gh auth setup-git
git pull --rebase origin main
git push --set-upstream origin "${branch}"

body=$(mktemp)
trap 'rm -f "${body}"' EXIT
cat >"${body}" <<'EOF'
Refresh the selected UBI minor-release manifest indexes and regenerate both
native RPM/source locks using the repository resolver. Both base indexes must
include linux/amd64 and linux/arm64. PostgreSQL seeds and signing keys are unchanged.

Owner review required: compare package/source versions, licenses, architecture
differences, current supplier advisories, and all CI results. Prior image evidence
and vulnerability approvals do not apply to these changed subjects. No human
sign-off is supplied by this automation. Scanner gates remain unchanged.

CI is explicitly dispatched on this branch because token-created PR events may
require approval or not start automatically. Do not merge without passing checks
and maintainer review. This workflow never merges or publishes an image.
EOF
gh pr create --base main --head "${branch}" \
    --title 'fix(deps): refresh UBI bases and artifact locks' --body-file "${body}"
gh workflow run ci.yml --ref "${branch}"
