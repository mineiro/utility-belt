.PHONY: prepare srpm

# COPR passes `spec` and `outdir` when using SCM + make_srpm.
specfile = $(notdir $(spec))

define is_rust_vendor_spec
	[ -n "$(spec)" ] && rpmspec -P "./$(specfile)" | grep -q '^Source1:' && \
	rpmspec -P "./$(specfile)" | grep -Eq '^BuildRequires:[[:space:]]+(cargo|cargo-rpm-macros|rust|rust-packaging)([[:space:]]|$$)'
endef

define is_go_vendor_spec
	[ -n "$(spec)" ] && rpmspec -P "./$(specfile)" | grep -q '^Source1:' && \
	rpmspec -P "./$(specfile)" | grep -Eq '^BuildRequires:[[:space:]]+golang([[:space:]]|$$)'
endef

prepare:
	@pkgs="rpm-build rpmdevtools"; \
	if $(is_rust_vendor_spec); then \
		pkgs="$$pkgs cargo"; \
	fi; \
	if $(is_go_vendor_spec); then \
		pkgs="$$pkgs golang"; \
	fi; \
	dnf -y install --setopt=install_weak_deps=0 --nodocs $$pkgs

srpm: prepare
	@test -n "$(spec)" || { echo "COPR did not pass 'spec'"; exit 1; }
	@test -n "$(outdir)" || { echo "COPR did not pass 'outdir'"; exit 1; }
	@if $(is_rust_vendor_spec) || $(is_go_vendor_spec); then \
		spectool -g --source 0 -R "./$(specfile)"; \
	else \
		spectool -g -R "./$(specfile)"; \
	fi
	@if ls ./patches/*.patch >/dev/null 2>&1; then \
		cp -f ./patches/*.patch ./; \
	fi
	@if ls ./patches/*.diff >/dev/null 2>&1; then \
		cp -f ./patches/*.diff ./; \
	fi
	@if $(is_rust_vendor_spec); then \
		if ! command -v cargo >/dev/null 2>&1; then \
			echo "cargo is required to generate vendored Rust sources for ./$(specfile)"; \
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
		( cd "$$srcdir" && if ! cargo vendor --locked vendor >/dev/null; then \
			echo "cargo vendor --locked failed for ./$(specfile), retrying without --locked" >&2; \
			cargo vendor vendor >/dev/null; \
		fi ); \
		tar -cJf "./$$vendor_name" -C "$$srcdir" vendor; \
		rm -rf "$$tmpdir"; \
		trap - EXIT; \
	fi
	@if $(is_go_vendor_spec); then \
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
		( cd "$$srcdir" && GO111MODULE=on go mod vendor ); \
		tar -cJf "./$$vendor_name" -C "$$srcdir" vendor; \
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
