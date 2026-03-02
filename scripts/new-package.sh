#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/new-package.sh [--template <generic|go|rust>] <package-name> <upstream-git-url> [upstream-releases-url]

Examples:
  scripts/new-package.sh trivy https://github.com/aquasecurity/trivy.git https://github.com/aquasecurity/trivy/releases
  scripts/new-package.sh --template rust grype https://github.com/anchore/grype.git
USAGE
}

template="generic"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --template)
      template="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      break
      ;;
  esac
done

if [[ $# -lt 2 || $# -gt 3 ]]; then
  usage
  exit 1
fi

pkg="$1"
upstream_git="$2"
upstream_releases="${3:-}"

case "$template" in
  generic|go|rust) ;;
  *)
    echo "Unsupported template: $template"
    exit 1
    ;;
esac

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
template_dir="${repo_root}/templates/package-${template}"
pkg_dir="${repo_root}/packages/${pkg}"

[[ -d "${template_dir}" ]] || { echo "Template not found: ${template_dir}"; exit 1; }
if [[ -e "${pkg_dir}" ]]; then
  echo "Package directory already exists: ${pkg_dir}"
  exit 1
fi

cp -a "${template_dir}" "${pkg_dir}"
mv "${pkg_dir}/pkgname.spec" "${pkg_dir}/${pkg}.spec"

sed -i \
  -e "s/^PACKAGE_NAME=.*/PACKAGE_NAME=${pkg}/" \
  -e "s/^SPEC_FILE=.*/SPEC_FILE=${pkg}.spec/" \
  -e "s|^UPSTREAM_GIT=.*|UPSTREAM_GIT=${upstream_git}|" \
  -e "s|^UPSTREAM_RELEASES=.*|UPSTREAM_RELEASES=${upstream_releases}|" \
  -e "s/^COPR_PACKAGE=.*/COPR_PACKAGE=${pkg}/" \
  -e "s|^COPR_SUBDIR=.*|COPR_SUBDIR=packages/${pkg}|" \
  "${pkg_dir}/package.env"

sed -i -e "s/^Name:.*/Name:           ${pkg}/" "${pkg_dir}/${pkg}.spec"

cat > "${pkg_dir}/README.md" <<NOTE
# ${pkg}

Starter packaging directory for \`${pkg}\`.

Template: \`${template}\`

Update \`${pkg}.spec\` and \`package.env\` before first build.
NOTE

echo "Created ${pkg_dir}"
