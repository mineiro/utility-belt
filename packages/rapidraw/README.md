# rapidraw

RPM packaging directory for `RapidRAW` 1.5.1.

Template: `generic`

Upstream:

- Git: https://github.com/CyberTimon/RapidRAW
- Releases: https://github.com/CyberTimon/RapidRAW/releases

Notes:

- Source build of the upstream Tauri application, not a repack of the
  Ubuntu-named GitHub release RPM assets.
- Uses vendored Rust crates and a vendored offline npm cache generated from
  upstream's `package-lock.json`.
- Patches the Linux build to use Fedora's system `onnxruntime` instead of
  downloading a prebuilt shared library during `build.rs`.
