# AGENTS.md

Session handoff notes for this repository.

## Intent

`utility-belt` is a Fedora RPM packaging monorepo for useful tools and
applications not yet available (or not current enough) in Fedora repos,
ranging from system utilities and terminal apps to developer and
infrastructure tooling.

## Conventions

- One package per `packages/<name>/` directory
- Prefer stable release specs first, `-git` variants later
- Keep package-specific patches in `patches/`
- Use `%autorelease` + `%autochangelog` for new specs
- Validate via `make check-specs` before pushes
- Validate SRPM + mock before COPR webhooks/auto-rebuild

## Core commands

```bash
make list
make check-specs
make srpm PACKAGE=<name>
make srpm-all
./scripts/mock-matrix-build.sh --all-packages
./scripts/copr-chain-build.sh <owner>/<project> <pkg1> <pkg2> ...
```

## Notes

- `.copr/Makefile` supports vendored Rust `Source1` generation for `%cargo_prep` specs.
- Keep `package.env` metadata updated; scripts rely on it for automation.
