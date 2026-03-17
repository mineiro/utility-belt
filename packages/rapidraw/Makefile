SHELL := /bin/bash

SPEC ?= $(firstword $(wildcard *.spec))
OUTDIR ?= $(CURDIR)/../../dist/srpm
SOURCEDIR ?= $(CURDIR)/sources
PATCHDIR ?= $(CURDIR)/patches

.PHONY: srpm vendor

srpm:
	@test -n "$(SPEC)" || { echo "No .spec file found"; exit 1; }
	@mkdir -p "$(OUTDIR)" "$(SOURCEDIR)"
	@if ls "$(PATCHDIR)"/*.patch >/dev/null 2>&1; then \
		cp -f "$(PATCHDIR)"/*.patch "$(SOURCEDIR)"/; \
	fi
	spectool -g --source 0 -C "$(SOURCEDIR)" "$(SPEC)"
	@if rpmspec -P "$(SPEC)" | grep -q '^Source3:'; then \
		spectool -g --source 3 -C "$(SOURCEDIR)" "$(SPEC)"; \
	fi
	$(MAKE) vendor SPEC="$(SPEC)" SOURCEDIR="$(SOURCEDIR)"
	rpmbuild -bs \
		--define "_sourcedir $(SOURCEDIR)" \
		--define "_specdir $(CURDIR)" \
		--define "_builddir $(CURDIR)" \
		--define "_srcrpmdir $(OUTDIR)" \
		--define "_rpmdir $(CURDIR)" \
		--define "_buildrootdir $(CURDIR)/.build" \
		"$(SPEC)"

vendor:
	@set -e; \
	src0_url="$$(rpmspec -P "$(SPEC)" | awk '/^Source0:[[:space:]]*/ { print $$2; exit }')"; \
	rust_vendor_url="$$(rpmspec -P "$(SPEC)" | awk '/^Source1:[[:space:]]*/ { print $$2; exit }')"; \
	node_vendor_url="$$(rpmspec -P "$(SPEC)" | awk '/^Source2:[[:space:]]*/ { print $$2; exit }')"; \
	submodule_url="$$(rpmspec -P "$(SPEC)" | awk '/^Source3:[[:space:]]*/ { print $$2; exit }')"; \
	src0_name="$${src0_url##*/}"; \
	rust_vendor_name="$${rust_vendor_url##*/}"; \
	node_vendor_name="$${node_vendor_url##*/}"; \
	submodule_name="$${submodule_url##*/}"; \
	helper="../../scripts/generate-npm-cache-from-lockfile.sh"; \
	if [ -z "$$rust_vendor_name" ] && [ -z "$$node_vendor_name" ]; then \
		echo "No vendor tarballs defined in $(SPEC), skipping vendor generation"; \
		exit 0; \
	fi; \
	[ -x "$$helper" ] || helper="./scripts/generate-npm-cache-from-lockfile.sh"; \
	[ -x "$$helper" ] || { echo "Node cache helper not found: ../../scripts/generate-npm-cache-from-lockfile.sh"; exit 1; }; \
	src0_path="$(SOURCEDIR)/$$src0_name"; \
	[ -f "$$src0_path" ] || { echo "Source0 not found: $$src0_path"; exit 1; }; \
	submodule_path="$(SOURCEDIR)/$$submodule_name"; \
	if [ -n "$$submodule_name" ]; then \
		[ -f "$$submodule_path" ] || { echo "Source3 not found: $$submodule_path"; exit 1; }; \
	fi; \
	tmpdir="$$(mktemp -d)"; \
	trap 'rm -rf "$$tmpdir"' EXIT; \
	tar -xf "$$src0_path" -C "$$tmpdir"; \
	srcdir="$$(find "$$tmpdir" -mindepth 1 -maxdepth 1 -type d | head -1)"; \
	[ -n "$$srcdir" ] || { echo "Failed to locate extracted source dir for vendoring"; exit 1; }; \
	if [ -n "$$submodule_name" ]; then \
		rm -rf "$$srcdir/src-tauri/rawler"; \
		mkdir -p "$$srcdir/src-tauri/rawler"; \
		tar -xf "$$submodule_path" --strip-components=1 -C "$$srcdir/src-tauri/rawler"; \
	fi; \
	if [ -n "$$rust_vendor_name" ]; then \
		command -v cargo >/dev/null 2>&1 || { echo "cargo is required to generate $$rust_vendor_name"; exit 1; }; \
		( cd "$$srcdir/src-tauri" && if ! CARGO_HOME="$$tmpdir/cargo-home" cargo vendor --locked vendor >/dev/null; then \
			echo "cargo vendor --locked failed for $(SPEC), retrying without --locked" >&2; \
			CARGO_HOME="$$tmpdir/cargo-home" cargo vendor vendor >/dev/null; \
		fi ); \
		tar -cJf "$(SOURCEDIR)/$$rust_vendor_name" -C "$$srcdir/src-tauri" vendor; \
		echo "Generated $(SOURCEDIR)/$$rust_vendor_name"; \
	fi; \
	if [ -n "$$node_vendor_name" ]; then \
		command -v npm >/dev/null 2>&1 || { echo "npm is required to generate $$node_vendor_name"; exit 1; }; \
		[ -f "$$srcdir/package-lock.json" ] || { echo "Missing package-lock.json in $$srcdir"; exit 1; }; \
		"$$helper" "$$srcdir/package-lock.json" "$$tmpdir/node-vendor/npm-cache"; \
		tar -cJf "$(SOURCEDIR)/$$node_vendor_name" -C "$$tmpdir/node-vendor" npm-cache; \
		echo "Generated $(SOURCEDIR)/$$node_vendor_name"; \
	fi; \
	rm -rf "$$tmpdir"; \
	trap - EXIT
