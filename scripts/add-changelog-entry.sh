#!/usr/bin/env bash
# Prepend a %changelog entry for the spec's current version-release.
#
#   scripts/add-changelog-entry.sh <spec> <message>
set -euo pipefail

[[ $# -eq 2 ]] || { echo "usage: $0 <spec> <message>" >&2; exit 2; }
spec="$1"
message="$2"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

evr="$(rpmspec -q --srpm --undefine dist --qf '%{version}-%{release}' "${spec}")"
packager="$(git -C "${repo_root}" config user.name) <$(git -C "${repo_root}" config user.email)>"
header="* $(LC_ALL=C date '+%a %b %d %Y') ${packager} - ${evr}"

grep -q '^%changelog$' "${spec}" || { echo "${spec}: no %changelog section" >&2; exit 1; }
awk -v header="${header}" -v message="- ${message}" '
  { print }
  /^%changelog$/ && !done { print header; print message; print ""; done = 1 }
' "${spec}" > "${spec}.tmp"
mv "${spec}.tmp" "${spec}"
