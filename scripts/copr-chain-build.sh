#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${repo_root}/scripts/package-release-support.sh"

usage() {
  cat <<'USAGE'
Queue ordered COPR builds using --after-build-id chaining.

Usage:
  scripts/copr-chain-build.sh <owner/project> [options] <package> [<package> ...]

Options:
  --after-build-id <id>      Start chain after existing build id
  --x86_64-only              Use only fedora-42/43/44/rawhide x86_64 chroots
  --aarch64-only             Use only fedora-42/43/44/rawhide aarch64 chroots
  --chroot <name>            Explicit chroot (repeatable)
  --background               Submit as background jobs
  -h, --help                 Show help
USAGE
}

[[ $# -ge 2 ]] || { usage; exit 1; }
project="$1"
shift

after_build_id=""
background=0
explicit_chroots=0

chroots=()
packages=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --after-build-id)
      after_build_id="${2:-}"
      [[ -n "${after_build_id}" ]] || { echo "--after-build-id requires a value"; exit 1; }
      shift 2
      ;;
    --x86_64-only)
      chroots=(fedora-42-x86_64 fedora-43-x86_64 fedora-44-x86_64 fedora-rawhide-x86_64)
      explicit_chroots=1
      shift
      ;;
    --aarch64-only)
      chroots=(fedora-42-aarch64 fedora-43-aarch64 fedora-44-aarch64 fedora-rawhide-aarch64)
      explicit_chroots=1
      shift
      ;;
    --chroot)
      val="${2:-}"
      [[ -n "${val}" ]] || { echo "--chroot requires a value"; exit 1; }
      chroots+=("${val}")
      explicit_chroots=1
      shift 2
      ;;
    --background)
      background=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      while [[ $# -gt 0 ]]; do
        packages+=("$1")
        shift
      done
      ;;
    -* )
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
    *)
      packages+=("$1")
      shift
      ;;
  esac
done

[[ ${#packages[@]} -gt 0 ]] || { echo "No packages specified"; exit 1; }

if [[ ${explicit_chroots} -eq 0 ]]; then
  chroots=(
    fedora-42-x86_64 fedora-43-x86_64 fedora-44-x86_64 fedora-rawhide-x86_64
    fedora-42-aarch64 fedora-43-aarch64 fedora-44-aarch64 fedora-rawhide-aarch64
  )
fi

prev="${after_build_id}"
submitted=0
for pkg in "${packages[@]}"; do
  filtered_chroots=()
  for c in "${chroots[@]}"; do
    if package_supports_chroot "${pkg}" "${c}"; then
      filtered_chroots+=("${c}")
    else
      printf 'Skipping %s in %s (unsupported by package.env)\n' "${pkg}" "${c}"
    fi
  done

  if [[ ${#filtered_chroots[@]} -eq 0 ]]; then
    printf 'Skipping %s: no selected chroots support this package\n' "${pkg}"
    continue
  fi

  build_opts=()
  for c in "${filtered_chroots[@]}"; do
    build_opts+=( -r "$c" )
  done
  if [[ ${background} -eq 1 ]]; then
    build_opts+=( --background )
  fi

  cmd=(copr-cli build-package "$project" --name "$pkg" --nowait)
  cmd+=("${build_opts[@]}")
  if [[ -n "${prev}" ]]; then
    cmd+=(--after-build-id "$prev")
  fi

  out="$("${cmd[@]}")"
  id="$(printf '%s\n' "$out" | sed -n 's/^Created builds: //p' | tail -n1)"
  [[ -n "$id" ]] || { echo "Failed to parse build id for $pkg"; printf '%s\n' "$out"; exit 1; }
  printf '%s -> %s\n' "$pkg" "$id"
  prev="$id"
  submitted=1
done

if [[ ${submitted} -eq 1 ]]; then
  printf 'Final build id: %s\n' "$prev"
else
  printf 'No builds submitted\n'
fi
