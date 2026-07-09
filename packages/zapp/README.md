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
