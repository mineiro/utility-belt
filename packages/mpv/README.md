# mpv

RPM packaging directory for `mpv` 0.41.0.

Template: `generic`

Upstream:

- Git: https://github.com/mpv-player/mpv.git
- Releases: https://github.com/mpv-player/mpv/releases

Notes:

- Follows Fedora's current package split: `mpv`, `mpv-libs`, and `mpv-devel`.
- Spec is based on Fedora rawhide's `0.41.0` packaging, adapted to this repo's
  `%autorelease` and `%autochangelog` conventions.
- Release base 3 makes the rawhide FFmpeg 9 rebuild newer than the previously
  published release 2, so existing installations receive it as an upgrade.
