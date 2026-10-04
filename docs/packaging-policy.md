# Packaging Policy

This repo is packaging infrastructure, not an upstream source mirror.

## Rules

1. One RPM package per directory under `packages/<name>/`.
2. Keep package-specific patches under `packages/<name>/patches/`.
3. Prefer stable release packages first; add `-git` variants only when needed.
4. Avoid vendoring unless Fedora packaging/build constraints require it.
5. If vendoring is required, document rationale in spec and declare `Provides: bundled(<name>)` where applicable.
6. Use an explicit `Release: N%{?dist}` and a maintained `%changelog`. COPR's
   `make_srpm` path does not process `%autorelease`, so it never advanced and
   `%autochangelog` shipped a placeholder entry. Every build-relevant change
   to a package needs a new Version or Release: `scripts/bump-version.sh`
   resets Release to 1, `scripts/bump-release.sh <pkg> "<reason>"` raises it
   for same-version rebuilds, and both add the changelog entry. CI
   (`scripts/check-nvr.sh`) and `scripts/copr-chain-build.sh` refuse changes
   or submissions that would reuse a published version-release.
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
