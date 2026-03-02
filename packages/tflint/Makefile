SHELL := /bin/bash

SPEC ?= $(firstword $(wildcard *.spec))
OUTDIR ?= $(CURDIR)/../../dist/srpm
SOURCEDIR ?= $(CURDIR)/sources

.PHONY: srpm vendor

srpm:
	@test -n "$(SPEC)" || { echo "No .spec file found"; exit 1; }
	@mkdir -p "$(OUTDIR)" "$(SOURCEDIR)"
	spectool -g -C "$(SOURCEDIR)" "$(SPEC)"
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
	@vendor_name="$$(rpmspec -P "$(SPEC)" | awk '/^Source1:[[:space:]]*/ { print $$2; exit }' | xargs basename)"; \
	src0_name="$$(rpmspec -P "$(SPEC)" | awk '/^Source0:[[:space:]]*/ { print $$2; exit }' | xargs basename)"; \
	if [ -z "$$vendor_name" ]; then \
		echo "No Source1 vendor tarball defined in $(SPEC), skipping vendor generation"; \
		exit 0; \
	fi; \
	command -v go >/dev/null 2>&1 || { echo "go is required to generate $$vendor_name"; exit 1; }; \
	src0_path="$(SOURCEDIR)/$$src0_name"; \
	[ -f "$$src0_path" ] || { echo "Source0 not found: $$src0_path"; exit 1; }; \
	tmpdir="$$(mktemp -d)"; \
	trap 'rm -rf "$$tmpdir"' EXIT; \
	tar -xf "$$src0_path" -C "$$tmpdir"; \
	srcdir="$$(find "$$tmpdir" -mindepth 1 -maxdepth 1 -type d | head -1)"; \
	[ -n "$$srcdir" ] || { echo "Failed to locate extracted source dir for vendoring"; exit 1; }; \
	( cd "$$srcdir" && GO111MODULE=on go mod vendor ); \
	tar -cJf "$(SOURCEDIR)/$$vendor_name" -C "$$srcdir" vendor; \
	rm -rf "$$tmpdir"; \
	trap - EXIT; \
	echo "Generated $(SOURCEDIR)/$$vendor_name"
