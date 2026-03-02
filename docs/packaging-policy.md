# Packaging Policy

This repo is packaging infrastructure, not an upstream source mirror.

## Rules

1. One RPM package per directory under `packages/<name>/`.
2. Keep package-specific patches under `packages/<name>/patches/`.
3. Prefer stable release packages first; add `-git` variants only when needed.
4. Avoid vendoring unless Fedora packaging/build constraints require it.
5. If vendoring is required, document rationale in spec and declare `Provides: bundled(<name>)` where applicable.
6. Use `Release: %autorelease` and `%autochangelog` unless there is a strong reason not to.
7. Use Fedora conditionals only when necessary and document why.
8. Validate with `rpmbuild` and `mock` before enabling COPR auto-rebuilds.

## Dependency and rollout strategy

- Build in dependency order when introducing a stack (e.g. libraries before consuming CLIs).
- For multi-arch rollout, stabilize x86_64 first, then trigger aarch64-only chains.
- Keep compatibility-pinned legacy packages separate from forward-moving stacks.
- Do not force ABI compatibility assumptions across major upstream families.

## Packaging taxonomy

Keep package intent explicit in `README.md` and `package.env`:

- security scanners
- IaC tooling
- Kubernetes/cluster tooling
- cloud CLIs
- policy/compliance tooling
- observability/operations tooling
