# keylight-control

Fedora RPM packaging for the `sandwichfarm/keylight-control` desktop app.

The package installs:

- `/usr/bin/keylight-controller`
- `/usr/share/keylight-control/src`
- `/usr/share/applications/keylight-controller.desktop`

Packaging notes:

- Ships the upstream Python source tree as a private application directory to
  avoid leaking its generic module names (`core`, `ui`, `utils`) into the
  global Python module path.
- Uses the tagged source release (`v1.2.0`) rather than the upstream
  prebuilt PyInstaller binary.
- Normalizes the broken upstream desktop `Exec` entry and package launcher
  version at build/install time.
