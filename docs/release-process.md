# Release Process

## Manual flow

1. Check upstream versions:
   - `./scripts/check-upstream-versions.sh --changed-only`
   - `./scripts/check-upstream-versions.sh --package <name>`
2. Update package spec (`Version`, `Source`, deps, patches)
   - If upstream now requires a newer Fedora toolchain, set
     `SUPPORTED_FEDORA_RELEASES` in `package.env` and verify older chroots are
     intentionally skipped.
3. Build SRPM:
   - `make srpm PACKAGE=<name>`
4. Validate with `mock` (at least Fedora 43/44 x86_64)
5. Commit and push
6. Trigger COPR build
7. Run repoclosure and install smoke checks

## Multi-arch rollout guidance

- Use x86_64 as baseline to validate packaging logic.
- Use aarch64 chain builds only after x86_64 is stable.
- Keep known legacy compatibility packages out of forward-only chains.

## Suggested gates

1. `make check-specs`
2. `mock --rebuild` across target Fedora releases
3. COPR build success for target chroots
4. `repoclosure` on COPR repo
5. install smoke in clean containers/VMs
