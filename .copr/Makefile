.PHONY: prepare srpm

# COPR passes `spec` and `outdir` when using SCM + make_srpm.
specfile = $(notdir $(spec))
GO_VENDOR_TOOLCHAIN ?= auto

define is_rust_vendor_spec
	[ -n "$(spec)" ] && rpmspec -P "./$(specfile)" | grep -q '^Source1:' && \
	rpmspec -P "./$(specfile)" | grep -Eq '^BuildRequires:[[:space:]]+(cargo|cargo-rpm-macros|rust|rust-packaging)([[:space:]]|$$)'
endef

define is_go_vendor_spec
	[ -n "$(spec)" ] && rpmspec -P "./$(specfile)" | grep -q '^Source1:' && \
	rpmspec -P "./$(specfile)" | grep -Eq '^BuildRequires:[[:space:]]+golang([[:space:]]|$$)'
endef

define is_node_vendor_spec
	[ -n "$(spec)" ] && rpmspec -P "./$(specfile)" | grep -q '^Source2:' && \
	rpmspec -P "./$(specfile)" | grep -Eq '^BuildRequires:[[:space:]]+nodejs([[:space:]]|$$)'
endef

prepare:
	@pkgs="rpm-build rpmdevtools"; \
	if $(is_rust_vendor_spec); then \
		pkgs="$$pkgs cargo"; \
	fi; \
	if $(is_go_vendor_spec); then \
		pkgs="$$pkgs golang"; \
	fi; \
	if $(is_node_vendor_spec); then \
		pkgs="$$pkgs jq nodejs npm"; \
	fi; \
	dnf -y install --setopt=install_weak_deps=0 --nodocs $$pkgs

srpm: prepare
	@test -n "$(spec)" || { echo "COPR did not pass 'spec'"; exit 1; }
	@test -n "$(outdir)" || { echo "COPR did not pass 'outdir'"; exit 1; }
	@if $(is_rust_vendor_spec) || $(is_go_vendor_spec) || $(is_node_vendor_spec); then \
		spectool -g --source 0 -R "./$(specfile)"; \
	else \
		spectool -g -R "./$(specfile)"; \
	fi
	@if rpmspec -P "./$(specfile)" | grep -q '^Source3:'; then \
		spectool -g --source 3 -R "./$(specfile)"; \
	fi
	@if ls ./patches/*.patch >/dev/null 2>&1; then \
		cp -f ./patches/*.patch ./; \
	fi
	@if ls ./patches/*.diff >/dev/null 2>&1; then \
		cp -f ./patches/*.diff ./; \
	fi
	@if $(is_rust_vendor_spec); then \
		set -e; \
		if ! command -v cargo >/dev/null 2>&1; then \
			echo "cargo is required to generate vendored Rust sources for ./$(specfile)"; \
			exit 1; \
		fi; \
		vendor_name="$$(rpmspec -P "./$(specfile)" | awk '/^Source1:[[:space:]]*/ { print $$2; exit }' | xargs basename)"; \
		src0_name="$$(rpmspec -P "./$(specfile)" | awk '/^Source0:[[:space:]]*/ { print $$2; exit }' | xargs basename)"; \
		submodule_url="$$(rpmspec -P "./$(specfile)" | awk '/^Source3:[[:space:]]*/ { print $$2; exit }')"; \
		submodule_name="$${submodule_url##*/}"; \
		tmpdir="$$(mktemp -d)"; \
		rpm_sourcedir="$$(rpm --eval '%{_sourcedir}' 2>/dev/null || true)"; \
		src0_path="./$$src0_name"; \
		submodule_path="./$$submodule_name"; \
		trap 'rm -rf "$$tmpdir"' EXIT; \
		if [ ! -f "$$src0_path" ] && [ -f "./sources/$$src0_name" ]; then \
			src0_path="./sources/$$src0_name"; \
		fi; \
		if [ ! -f "$$src0_path" ] && [ -f "./SOURCES/$$src0_name" ]; then \
			src0_path="./SOURCES/$$src0_name"; \
		fi; \
		if [ ! -f "$$src0_path" ] && [ -n "$$rpm_sourcedir" ] && [ -f "$$rpm_sourcedir/$$src0_name" ]; then \
			src0_path="$$rpm_sourcedir/$$src0_name"; \
		fi; \
		if [ ! -f "$$src0_path" ] && [ -f "$$HOME/rpmbuild/SOURCES/$$src0_name" ]; then \
			src0_path="$$HOME/rpmbuild/SOURCES/$$src0_name"; \
		fi; \
		if [ "$$src0_path" != "./$$src0_name" ]; then \
			cp -f "$$src0_path" "./$$src0_name"; \
			src0_path="./$$src0_name"; \
		fi; \
		if [ -n "$$submodule_name" ] && [ ! -f "$$submodule_path" ] && [ -f "./sources/$$submodule_name" ]; then \
			submodule_path="./sources/$$submodule_name"; \
		fi; \
		if [ -n "$$submodule_name" ] && [ ! -f "$$submodule_path" ] && [ -f "./SOURCES/$$submodule_name" ]; then \
			submodule_path="./SOURCES/$$submodule_name"; \
		fi; \
		if [ -n "$$submodule_name" ] && [ ! -f "$$submodule_path" ] && [ -n "$$rpm_sourcedir" ] && [ -f "$$rpm_sourcedir/$$submodule_name" ]; then \
			submodule_path="$$rpm_sourcedir/$$submodule_name"; \
		fi; \
		if [ -n "$$submodule_name" ] && [ ! -f "$$submodule_path" ] && [ -f "$$HOME/rpmbuild/SOURCES/$$submodule_name" ]; then \
			submodule_path="$$HOME/rpmbuild/SOURCES/$$submodule_name"; \
		fi; \
		if [ -n "$$submodule_name" ] && [ "$$submodule_path" != "./$$submodule_name" ]; then \
			cp -f "$$submodule_path" "./$$submodule_name"; \
			submodule_path="./$$submodule_name"; \
		fi; \
		[ -f "$$src0_path" ] || { echo "Downloaded Source0 not found for vendoring: $$src0_name"; exit 1; }; \
		tar -xf "$$src0_path" -C "$$tmpdir"; \
		srcdir="$$(find "$$tmpdir" -mindepth 1 -maxdepth 1 -type d | head -1)"; \
		[ -n "$$srcdir" ] || { echo "Failed to locate extracted source dir for vendoring"; exit 1; }; \
		if [ -n "$$submodule_name" ]; then \
			[ -f "$$submodule_path" ] || { echo "Downloaded Source3 not found for vendoring: $$submodule_name"; exit 1; }; \
			rm -rf "$$srcdir/src-tauri/rawler"; \
			mkdir -p "$$srcdir/src-tauri/rawler"; \
			tar -xf "$$submodule_path" --strip-components=1 -C "$$srcdir/src-tauri/rawler"; \
		fi; \
		manifest_dir="$$srcdir"; \
		if [ ! -f "$$manifest_dir/Cargo.toml" ] && [ -f "$$srcdir/src-tauri/Cargo.toml" ]; then \
			manifest_dir="$$srcdir/src-tauri"; \
		fi; \
		[ -f "$$manifest_dir/Cargo.toml" ] || { echo "Failed to locate Cargo.toml for vendoring in $$srcdir"; exit 1; }; \
		( cd "$$manifest_dir" && if ! cargo vendor --locked vendor >/dev/null; then \
			echo "cargo vendor --locked failed for ./$(specfile), retrying without --locked" >&2; \
			cargo vendor vendor >/dev/null; \
		fi ); \
		tar -cJf "./$$vendor_name" -C "$$manifest_dir" vendor; \
		rm -rf "$$tmpdir"; \
		trap - EXIT; \
	fi
	@if $(is_go_vendor_spec); then \
		set -e; \
		if ! command -v go >/dev/null 2>&1; then \
			echo "go is required to generate vendored Go sources for ./$(specfile)"; \
			exit 1; \
		fi; \
		vendor_name="$$(rpmspec -P "./$(specfile)" | awk '/^Source1:[[:space:]]*/ { print $$2; exit }' | xargs basename)"; \
		src0_name="$$(rpmspec -P "./$(specfile)" | awk '/^Source0:[[:space:]]*/ { print $$2; exit }' | xargs basename)"; \
		tmpdir="$$(mktemp -d)"; \
		rpm_sourcedir="$$(rpm --eval '%{_sourcedir}' 2>/dev/null || true)"; \
		src0_path="./$$src0_name"; \
		trap 'rm -rf "$$tmpdir"' EXIT; \
		if [ ! -f "$$src0_path" ] && [ -f "./sources/$$src0_name" ]; then \
			src0_path="./sources/$$src0_name"; \
		fi; \
		if [ ! -f "$$src0_path" ] && [ -f "./SOURCES/$$src0_name" ]; then \
			src0_path="./SOURCES/$$src0_name"; \
		fi; \
		if [ ! -f "$$src0_path" ] && [ -n "$$rpm_sourcedir" ] && [ -f "$$rpm_sourcedir/$$src0_name" ]; then \
			src0_path="$$rpm_sourcedir/$$src0_name"; \
		fi; \
		if [ ! -f "$$src0_path" ] && [ -f "$$HOME/rpmbuild/SOURCES/$$src0_name" ]; then \
			src0_path="$$HOME/rpmbuild/SOURCES/$$src0_name"; \
		fi; \
		if [ "$$src0_path" != "./$$src0_name" ]; then \
			cp -f "$$src0_path" "./$$src0_name"; \
			src0_path="./$$src0_name"; \
		fi; \
		[ -f "$$src0_path" ] || { echo "Downloaded Source0 not found for vendoring: $$src0_name"; exit 1; }; \
		tar -xf "$$src0_path" -C "$$tmpdir"; \
		srcdir="$$(find "$$tmpdir" -mindepth 1 -maxdepth 1 -type d | head -1)"; \
		[ -n "$$srcdir" ] || { echo "Failed to locate extracted source dir for vendoring"; exit 1; }; \
		( cd "$$srcdir" && GO111MODULE=on GOTOOLCHAIN="$(GO_VENDOR_TOOLCHAIN)" go mod vendor ); \
		tar -cJf "./$$vendor_name" -C "$$srcdir" vendor; \
		rm -rf "$$tmpdir"; \
		trap - EXIT; \
	fi
	@if $(is_node_vendor_spec); then \
		set -e; \
		if ! command -v jq >/dev/null 2>&1; then \
			echo "jq is required to generate vendored Node.js sources for ./$(specfile)"; \
			exit 1; \
		fi; \
		if ! command -v npm >/dev/null 2>&1; then \
			echo "npm is required to generate vendored Node.js sources for ./$(specfile)"; \
			exit 1; \
		fi; \
		vendor_name="$$(rpmspec -P "./$(specfile)" | awk '/^Source2:[[:space:]]*/ { print $$2; exit }' | xargs basename)"; \
		src0_name="$$(rpmspec -P "./$(specfile)" | awk '/^Source0:[[:space:]]*/ { print $$2; exit }' | xargs basename)"; \
		tmpdir="$$(mktemp -d)"; \
		rpm_sourcedir="$$(rpm --eval '%{_sourcedir}' 2>/dev/null || true)"; \
		src0_path="./$$src0_name"; \
		helper="../../scripts/generate-npm-cache-from-lockfile.sh"; \
		trap 'rm -rf "$$tmpdir"' EXIT; \
		if [ ! -f "$$src0_path" ] && [ -f "./sources/$$src0_name" ]; then \
			src0_path="./sources/$$src0_name"; \
		fi; \
		if [ ! -f "$$src0_path" ] && [ -f "./SOURCES/$$src0_name" ]; then \
			src0_path="./SOURCES/$$src0_name"; \
		fi; \
		if [ ! -f "$$src0_path" ] && [ -n "$$rpm_sourcedir" ] && [ -f "$$rpm_sourcedir/$$src0_name" ]; then \
			src0_path="$$rpm_sourcedir/$$src0_name"; \
		fi; \
		if [ ! -f "$$src0_path" ] && [ -f "$$HOME/rpmbuild/SOURCES/$$src0_name" ]; then \
			src0_path="$$HOME/rpmbuild/SOURCES/$$src0_name"; \
		fi; \
		if [ "$$src0_path" != "./$$src0_name" ]; then \
			cp -f "$$src0_path" "./$$src0_name"; \
			src0_path="./$$src0_name"; \
		fi; \
		[ -f "$$src0_path" ] || { echo "Downloaded Source0 not found for vendoring: $$src0_name"; exit 1; }; \
		[ -x "$$helper" ] || helper="./scripts/generate-npm-cache-from-lockfile.sh"; \
		[ -x "$$helper" ] || { echo "Node cache helper not found: ../../scripts/generate-npm-cache-from-lockfile.sh"; exit 1; }; \
		tar -xf "$$src0_path" -C "$$tmpdir"; \
		srcdir="$$(find "$$tmpdir" -mindepth 1 -maxdepth 1 -type d | head -1)"; \
		[ -n "$$srcdir" ] || { echo "Failed to locate extracted source dir for vendoring"; exit 1; }; \
		[ -f "$$srcdir/package-lock.json" ] || { echo "Missing package-lock.json in $$srcdir"; exit 1; }; \
		"$$helper" "$$srcdir/package-lock.json" "$$tmpdir/node-vendor/npm-cache"; \
		tar -cJf "./$$vendor_name" -C "$$tmpdir/node-vendor" npm-cache; \
		rm -rf "$$tmpdir"; \
		trap - EXIT; \
	fi
	rpmbuild -bs \
		--define "_sourcedir ${PWD}" \
		--define "_specdir ${PWD}" \
		--define "_builddir ${PWD}" \
		--define "_srcrpmdir $(outdir)" \
		--define "_rpmdir ${PWD}" \
		--define "_buildrootdir ${PWD}/.build" \
		"./$(specfile)"
