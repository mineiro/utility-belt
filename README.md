# utility-belt

Monorepo for Fedora RPM packaging of useful tools and applications, from
system utilities and terminal apps to developer, infrastructure, and other
handy packages.

This repository is intentionally structured as a packaging monorepo:

- One package per directory under `packages/`
- Shared build helpers and CI at repo root
- COPR builds use `SCM` + `make_srpm`
- Local testing uses `rpmbuild` and `mock`

## Layout

```text
.
├── .copr/                  # COPR make_srpm integration
├── .github/workflows/      # CI checks (spec parse, repoclosure)
├── docs/                   # Packaging policy, COPR setup, release workflow
├── scripts/                # Helpers (new package, version checks, mock matrix)
├── templates/              # Package templates (generic/go/rust)
└── packages/               # One directory per RPM source package
```

## Quick start

Install baseline packaging tools:

```bash
sudo dnf install -y rpm-build rpmdevtools mock rpmlint copr-cli git jq curl
```

List packages:

```bash
make list
```

Parse/lint specs:

```bash
make check-specs
```

Create a new package skeleton:

```bash
./scripts/new-package.sh --template go trivy https://github.com/aquasecurity/trivy.git https://github.com/aquasecurity/trivy/releases
```

Build one SRPM:

```bash
make srpm PACKAGE=trivy
```

Build all SRPMs:

```bash
make srpm-all
```

Run a matrix mock build:

```bash
./scripts/mock-matrix-build.sh --x86_64-only trivy
```

Queue ordered COPR builds:

```bash
./scripts/copr-chain-build.sh mineiro utility-belt --aarch64-only trivy grype syft
```

See `docs/` for workflow details.
