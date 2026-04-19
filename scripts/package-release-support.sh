#!/usr/bin/env bash

package_env_value() {
  local pkg="$1" key="$2" envf="${repo_root}/packages/${pkg}/package.env"
  [[ -f "${envf}" ]] || return 0
  awk -F= -v key="${key}" '$1 == key { sub(/^[^=]*=/, ""); print; exit }' "${envf}"
}

package_supported_fedora_releases() {
  local pkg="$1"
  package_env_value "${pkg}" SUPPORTED_FEDORA_RELEASES | tr ',;' '  '
}

package_supports_fedora_release() {
  local pkg="$1" release="$2" supported token
  supported="$(package_supported_fedora_releases "${pkg}")"
  if [[ -z "${supported//[[:space:]]/}" ]]; then
    return 0
  fi

  for token in ${supported}; do
    case "${token}" in
      all|"${release}")
        return 0
        ;;
    esac
  done

  return 1
}

fedora_release_from_chroot() {
  local chroot="$1"
  if [[ "${chroot}" =~ ^fedora-([0-9]+|rawhide)- ]]; then
    printf '%s\n' "${BASH_REMATCH[1]}"
    return 0
  fi
  return 1
}

package_supports_chroot() {
  local pkg="$1" chroot="$2" release
  release="$(fedora_release_from_chroot "${chroot}")" || return 0
  package_supports_fedora_release "${pkg}" "${release}"
}
