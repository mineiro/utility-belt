# zapp

RPM packaging directory for `zapp`.

Template: `rust`

Upstream:

- Git: https://github.com/zsa/zapp.git
- Releases: https://github.com/zsa/zapp/releases

Notes:

- Rust package with vendored crates in `Source1`.
- Installs upstream `udev/50-zsa.rules` so ZSA keyboards can be flashed
  without root after udev reloads the packaged rules.
- Upstream currently ships a v1.0.1 tarball with stale workspace package
  versions in `Cargo.lock`; the package syncs those values during prep and
  vendor tarball generation.
