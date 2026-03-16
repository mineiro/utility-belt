# zathura

RPM packaging directory for `zathura` 2026.02.22.

Template: `generic`

Upstream:

- Git: https://git.pwmt.org/pwmt/zathura
- Releases: https://pwmt.org/projects/zathura/download/

Notes:

- Follows Fedora's current subpackage split for the core viewer: `zathura`,
  `zathura-devel`, `zathura-plugins-all`, and shell completion subpackages.
- Requires the new date-based `girara` series; this repo packages that in
  `packages/girara`.
