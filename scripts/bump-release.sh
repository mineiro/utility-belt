#!/usr/bin/env bash
# Raise Release by one for a same-version rebuild and record why.
#
# Every rebuild needs a new version-release: DNF compares NEVRA, so a rebuild
# published under an existing one is never offered to systems that already
# have it installed.
#
#   scripts/bump-release.sh <package-name-or-dir> <reason>
set -euo pipefail

[[ $# -eq 2 ]] || { echo "usage: $0 <package-name-or-dir> <reason>" >&2; exit 2; }
target="$1"
reason="$2"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -d "${target}" ]]; then
  pkg_dir="$(cd "${target}" && pwd)"
else
  pkg_dir="${repo_root}/packages/${target}"
fi
spec="$(find "${pkg_dir}" -maxdepth 1 -type f -name '*.spec' | head -n1)"
[[ -n "${spec}" ]] || { echo "No .spec file found in ${pkg_dir}" >&2; exit 1; }

old="$(awk '/^Release:[[:space:]]+/ { print $2; exit }' "${spec}")"
[[ "${old}" =~ ^([0-9]+)%\{\?dist\}$ ]] || {
  echo "${spec}: expected 'Release: N%{?dist}', found '${old}'" >&2
  exit 1
}
new=$((BASH_REMATCH[1] + 1))
sed -i -E "0,/^Release:[[:space:]]+/{s|^Release:[[:space:]]+.*$|Release:        ${new}%{?dist}|}" "${spec}"
"${repo_root}/scripts/add-changelog-entry.sh" "${spec}" "${reason}"
echo "Updated ${spec#"${repo_root}"/}: Release ${BASH_REMATCH[1]} -> ${new}"
