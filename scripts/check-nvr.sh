#!/usr/bin/env bash
# A package change must carry a Version or Release bump.
#
# DNF compares NEVRA. A rebuild published under an existing version-release
# replaces those RPMs in COPR with different bits, and systems that already
# installed that version-release are never offered the rebuild. This is how
# the mpv FFmpeg rebuild in 2026-09 shipped without reaching anyone.
#
# Any change under packages/<name>/ counts, except README.md and package.env,
# which do not change what gets built.
#
#   scripts/check-nvr.sh <base-ref>
set -euo pipefail

base="${1:?usage: check-nvr.sh <base-ref>}"
if ! mergebase="$(git merge-base "${base}" HEAD 2>/dev/null)"; then
  echo "cannot find a merge base with ${base}; fetch more history" >&2
  exit 1
fi

changed="$(git diff --name-only "${mergebase}" HEAD -- packages/ |
  grep -Ev '^packages/[^/]+/(README\.md|package\.env)$' || true)"
if [[ -z "${changed}" ]]; then
  echo "no build-relevant package change; nothing to bump"
  exit 0
fi

field() { awk -v f="$1" '$1 == f ":" { print $2; exit }'; }
status=0
while read -r pkg; do
  spec="$(git ls-tree --name-only HEAD "packages/${pkg}/" | grep '\.spec$' | head -n1 || true)"
  if [[ -z "${spec}" ]]; then
    echo "${pkg}: package removed; nothing to bump"
    continue
  fi
  if ! old="$(git show "${mergebase}:${spec}" 2>/dev/null)"; then
    echo "${pkg}: new package"
    continue
  fi
  new="$(git show "HEAD:${spec}")"
  old_vr="$(field Version <<<"${old}")-$(field Release <<<"${old}")"
  new_vr="$(field Version <<<"${new}")-$(field Release <<<"${new}")"
  if [[ "${old_vr}" == "${new_vr}" ]]; then
    echo "${pkg}: files changed but Version-Release did not (${new_vr}):"
    grep "^packages/${pkg}/" <<<"${changed}" | sed 's/^/    /'
    echo "    Run scripts/bump-release.sh ${pkg} \"<reason>\" (or bump-version.sh)."
    status=1
  else
    echo "${pkg}: ok (${old_vr} -> ${new_vr})"
  fi
done < <(awk -F/ 'NF >= 3 { print $2 }' <<<"${changed}" | sort -u)
exit "${status}"
