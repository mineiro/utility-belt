#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${repo_root}/scripts/package-release-support.sh"

usage() {
  cat <<'USAGE'
Run mock builds across a Fedora/architecture matrix.

Usage:
  scripts/mock-matrix-build.sh [options] <package> [<package> ...]
  scripts/mock-matrix-build.sh [options] --all-packages

Options:
  --all-packages              Build every package under packages/
  --release <42|43|44|rawhide>  Target Fedora release (repeatable)
  --arch <x86_64|aarch64>    Target architecture (repeatable)
  --x86_64-only              Shortcut for --arch x86_64
  --aarch64-only             Shortcut for --arch aarch64
  --mode <chain|rebuild>     Build mode (default: chain)
  --addrepo <url>            Extra repository for mock buildroot (repeatable)
  --result-root <path>       Base output directory (default: repo/mock-results)
  --srpm-out <path>          SRPM output directory (default: repo/dist/srpm)
  --skip-srpm                Reuse existing SRPMs in --srpm-out
  --continue-on-failure      Continue remaining chroots if one fails
  --mock-arg <arg>           Extra argument passed to mock (repeatable)
  --help                     Show this help
USAGE
}

log() { printf '[matrix] %s\n' "$*"; }
die() { printf '[matrix] ERROR: %s\n' "$*" >&2; exit 1; }
require_cmd() { command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"; }

is_valid_release() { case "$1" in 42|43|44|rawhide) return 0;; *) return 1;; esac; }
is_valid_arch() { case "$1" in x86_64|aarch64) return 0;; *) return 1;; esac; }
require_value() { local opt="$1" val="${2:-}"; [[ -n "$val" ]] || die "${opt} requires a value"; }

release_set=0
arch_set=0
all_packages=0
skip_srpm=0
continue_on_failure=0
mode="chain"
result_root="${repo_root}/mock-results"
srpm_out="${repo_root}/dist/srpm"

declare -a releases=()
declare -a arches=()
declare -a package_args=()
declare -a extra_repos=()
declare -a mock_args=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all-packages) all_packages=1; shift ;;
    --release)
      require_value "$1" "${2:-}"
      is_valid_release "$2" || die "Unsupported release: $2"
      releases+=("$2"); release_set=1; shift 2 ;;
    --arch)
      require_value "$1" "${2:-}"
      is_valid_arch "$2" || die "Unsupported arch: $2"
      arches+=("$2"); arch_set=1; shift 2 ;;
    --x86_64-only)
      arches=(x86_64); arch_set=1; shift ;;
    --aarch64-only)
      arches=(aarch64); arch_set=1; shift ;;
    --mode)
      require_value "$1" "${2:-}"
      case "$2" in chain|rebuild) mode="$2";; *) die "Unsupported mode: $2";; esac
      shift 2 ;;
    --addrepo) require_value "$1" "${2:-}"; extra_repos+=("$2"); shift 2 ;;
    --result-root) require_value "$1" "${2:-}"; result_root="$2"; shift 2 ;;
    --srpm-out) require_value "$1" "${2:-}"; srpm_out="$2"; shift 2 ;;
    --skip-srpm) skip_srpm=1; shift ;;
    --continue-on-failure) continue_on_failure=1; shift ;;
    --mock-arg) require_value "$1" "${2:-}"; mock_args+=("$2"); shift 2 ;;
    --help|-h) usage; exit 0 ;;
    --) shift; while [[ $# -gt 0 ]]; do package_args+=("$1"); shift; done ;;
    -*) die "Unknown option: $1" ;;
    *) package_args+=("$1"); shift ;;
  esac
done

if [[ ${release_set} -eq 0 ]]; then releases=(42 43 44 rawhide); fi
if [[ ${arch_set} -eq 0 ]]; then arches=(x86_64 aarch64); fi

require_cmd make
require_cmd mock

if [[ ${all_packages} -eq 1 && ${#package_args[@]} -gt 0 ]]; then
  die "Use either explicit packages or --all-packages, not both"
fi

declare -a packages=()
if [[ ${all_packages} -eq 1 ]]; then
  mapfile -t packages < <(find "${repo_root}/packages" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort)
else
  packages=("${package_args[@]}")
fi

[[ ${#packages[@]} -gt 0 ]] || die "No packages selected"

for pkg in "${packages[@]}"; do
  [[ -d "${repo_root}/packages/${pkg}" ]] || die "Unknown package directory: packages/${pkg}"
  [[ -f "${repo_root}/packages/${pkg}/${pkg}.spec" ]] || die "Missing spec file: packages/${pkg}/${pkg}.spec"
done

mkdir -p "${srpm_out}" "${result_root}"

package_selected_for_releases() {
  local pkg="$1" rel
  for rel in "${releases[@]}"; do
    if package_supports_fedora_release "${pkg}" "${rel}"; then
      return 0
    fi
  done
  return 1
}

if [[ ${skip_srpm} -eq 0 ]]; then
  for pkg in "${packages[@]}"; do
    if ! package_selected_for_releases "${pkg}"; then
      log "Skipping SRPM: ${pkg} (not enabled for selected Fedora releases)"
      continue
    fi
    log "Building SRPM: ${pkg}"
    make -C "${repo_root}" srpm PACKAGE="${pkg}" OUTDIR="${srpm_out}"
  done
else
  log "Skipping SRPM build phase"
fi

declare -A srpm_by_pkg=()
for pkg in "${packages[@]}"; do
  if ! package_selected_for_releases "${pkg}"; then
    continue
  fi
  latest_srpm="$(
    find "${srpm_out}" -maxdepth 1 -type f -name "${pkg}-*.src.rpm" -printf '%T@ %p\n' 2>/dev/null \
      | awk -v pkg="${pkg}" '
          {
            path = $0
            sub(/^[^ ]+ /, "", path)
            file = path
            sub(/^.*\//, "", file)
            if (file ~ ("^" pkg "-[0-9].*\\.src\\.rpm$")) {
              print
            }
          }
        ' \
      | sort -nr \
      | head -n 1 \
      | cut -d' ' -f2-
  )"
  [[ -n "${latest_srpm}" ]] || die "No SRPM found for ${pkg} under ${srpm_out}"
  srpm_by_pkg["${pkg}"]="${latest_srpm}"
done

declare -a chroots=()
for rel in "${releases[@]}"; do
  for arch in "${arches[@]}"; do
    cfg="fedora-${rel}-${arch}"
    [[ -f "/etc/mock/${cfg}.cfg" ]] || die "Mock config not found: /etc/mock/${cfg}.cfg"
    chroots+=("${cfg}")
  done
done

declare -A chroot_status=()
run_stamp="$(date +%Y%m%d-%H%M%S)"
had_failure=0

for cfg in "${chroots[@]}"; do
  run_dir="${result_root}/${cfg}/matrix-${run_stamp}"
  mkdir -p "${run_dir}"

  log "Running ${mode} build in ${cfg}"

  cfg_packages=()
  cfg_srpms=()
  for pkg in "${packages[@]}"; do
    if package_supports_chroot "${pkg}" "${cfg}"; then
      [[ -n "${srpm_by_pkg[$pkg]:-}" ]] || die "No SRPM selected for ${pkg} in ${cfg}"
      cfg_packages+=("${pkg}")
      cfg_srpms+=("${srpm_by_pkg[$pkg]}")
    else
      log "Skipping ${pkg} in ${cfg} (unsupported by package.env)"
    fi
  done

  if [[ ${#cfg_srpms[@]} -eq 0 ]]; then
    chroot_status["${cfg}"]="skipped"
    log "Skipping ${cfg}: no selected packages support this chroot"
    continue
  fi

  extra_repo_args=()
  for repo in "${extra_repos[@]}"; do
    extra_repo_args+=(--addrepo "$repo")
  done

  if [[ "${mode}" == "chain" ]]; then
    mkdir -p "${run_dir}/localrepo"
    if mock --chain -r "${cfg}" --localrepo "${run_dir}/localrepo" "${extra_repo_args[@]}" "${mock_args[@]}" "${cfg_srpms[@]}"; then
      chroot_status["${cfg}"]="ok"
    else
      chroot_status["${cfg}"]="fail"
      had_failure=1
      if [[ ${continue_on_failure} -eq 0 ]]; then break; fi
    fi
  else
    rebuild_failed=0
    for i in "${!cfg_packages[@]}"; do
      pkg="${cfg_packages[$i]}"
      srpm="${cfg_srpms[$i]}"
      pkg_result_dir="${run_dir}/${pkg}"
      mkdir -p "${pkg_result_dir}"

      log "Rebuilding ${pkg} in ${cfg}"
      if ! mock -r "${cfg}" --resultdir "${pkg_result_dir}" "${extra_repo_args[@]}" "${mock_args[@]}" --rebuild "${srpm}"; then
        rebuild_failed=1
        had_failure=1
        if [[ ${continue_on_failure} -eq 0 ]]; then break; fi
      fi
    done

    if [[ ${rebuild_failed} -eq 0 ]]; then
      chroot_status["${cfg}"]="ok"
    else
      chroot_status["${cfg}"]="fail"
      if [[ ${continue_on_failure} -eq 0 ]]; then break; fi
    fi
  fi
done

printf '\n[matrix] Summary (%s mode):\n' "${mode}"
for cfg in "${chroots[@]}"; do
  status="${chroot_status[$cfg]:-not-run}"
  printf '[matrix]   %-24s %s\n' "${cfg}" "${status}"
done

if [[ ${had_failure} -ne 0 ]]; then exit 1; fi
log "All requested matrix builds completed successfully"
