# bluetui

RPM packaging directory for `bluetui`.

Template: `rust`

Upstream:

- Git: https://github.com/pythops/bluetui.git
- Releases: https://github.com/pythops/bluetui/releases

Notes:

- Rust package with vendored crates in `Source1`.
- Patch disables upstream `libdbus-sys` vendoring so the RPM links against Fedora's system `dbus` library.
