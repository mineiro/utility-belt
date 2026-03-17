# COPR Setup

This repo is designed for COPR `SCM` package entries (one entry per package directory).

## Recommended project layout

- COPR project name: `utility-belt`
- Chroots:
  - `fedora-42-x86_64`
  - `fedora-43-x86_64`
  - `fedora-44-x86_64`
  - `fedora-rawhide-x86_64`
  - `fedora-42-aarch64`
  - `fedora-43-aarch64`
  - `fedora-44-aarch64`
  - `fedora-rawhide-aarch64`

## Add a package from this monorepo

For each package directory:

- `Clone URL`: your Git repo URL
- `Committish`: `main`
- `Subdirectory`: `packages/<pkgname>`
- `Spec file`: `<pkgname>.spec`
- `Build source type`: `SCM`
- `Build SRPM with`: `make_srpm`

The shared `.copr/Makefile` handles SRPM generation inside COPR.

## Recommended sequence

1. Create package entry
2. Trigger one manual x86_64 build
3. Resolve dependency closure issues
4. Trigger aarch64-only rollout if needed
5. Enable webhook/auto-rebuild when stable

## Useful commands

```bash
# one package, x86_64 + aarch64 all chroots
copr-cli build-package <owner>/<project> --name <pkg>

# aarch64-only rollout
copr-cli build-package <owner>/<project> --name <pkg> \
  -r fedora-42-aarch64 -r fedora-43-aarch64 -r fedora-44-aarch64 -r fedora-rawhide-aarch64
```
