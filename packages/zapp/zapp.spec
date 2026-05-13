%global debug_package %{nil}
%{!?_udevrulesdir:%global _udevrulesdir %{_prefix}/lib/udev/rules.d}

Name:           zapp
Version:        1.0.1
Release:        %autorelease
Summary:        CLI tool for flashing ZSA keyboards

# Upstream licenses Zapp as MIT with the Commons Clause restriction.
License:        MIT AND LicenseRef-commons-clause
URL:            https://github.com/zsa/zapp
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
# Placeholder URL for a locally generated vendor tarball; SRPM helpers create
# the actual file before rpmbuild consumes it.
Source1:        https://example.invalid/%{name}-%{version}-vendor.tar.xz#/%{name}-%{version}-vendor.tar.xz

BuildRequires:  cargo
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  hidapi-devel
BuildRequires:  make
BuildRequires:  pkgconf-pkg-config
BuildRequires:  rust >= 1.85
BuildRequires:  systemd-rpm-macros

Requires:       systemd-udev

# Vendored Rust crates are used to keep SRPM and COPR builds reproducible while
# the dependency stack is not yet packaged in Fedora.
Provides:       bundled(crate(anyhow)) = 1.0.102
Provides:       bundled(crate(clap)) = 4.6.0
Provides:       bundled(crate(env_logger)) = 0.11.10
Provides:       bundled(crate(futures-lite)) = 2.6.1
Provides:       bundled(crate(hidapi)) = 2.6.5
Provides:       bundled(crate(indicatif)) = 0.17.11
Provides:       bundled(crate(nusb)) = 0.2.3
Provides:       bundled(crate(reqwest)) = 0.13.2
Provides:       bundled(crate(rustls)) = 0.23.37
Provides:       bundled(crate(serde)) = 1.0.228
Provides:       bundled(crate(serde_json)) = 1.0.149
Provides:       bundled(crate(thiserror)) = 2.0.18
Provides:       bundled(crate(tokio)) = 1.51.0

%description
Zapp is a command-line tool for flashing ZSA keyboards. It can flash local
firmware files, flash firmware from Oryx layout URLs, and update compatible
keyboards already running Oryx-built firmware.

%prep
%autosetup
# Upstream v1.0.1 updated workspace package versions but not Cargo.lock.
sed -i '/^name = "zapp"$/,/^dependencies = \[/ { s/^version = "1\.0\.0"$/version = "1.0.1"/ }' Cargo.lock
sed -i '/^name = "zapp-core"$/,/^dependencies = \[/ { s/^version = "0\.1\.0"$/version = "0.1.1"/ }' Cargo.lock
# Link against Fedora's shared hidapi instead of compiling the vendored C copy.
sed -i 's/^hidapi = "2"$/hidapi = { version = "2", default-features = false, features = ["linux-shared-hidraw"] }/' zapp-core/Cargo.toml
mkdir -p .cargo
cat > .cargo/config.toml <<'EOF'
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF
tar -xJf %{SOURCE1}

%build
%set_build_flags
export CARGO_HOME="$PWD/.cargo-home"
export RUSTFLAGS="${RUSTFLAGS:-%{build_rustflags}}"
cargo build --release --frozen --package %{name}

%install
install -Dpm0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}
install -Dpm0644 udev/50-zsa.rules %{buildroot}%{_udevrulesdir}/50-zsa.rules

%check
./target/release/%{name} --version | grep -q "%{name} %{version}"
grep -q 'ATTR{idVendor}=="3297"' udev/50-zsa.rules
grep -q 'ATTR{idVendor}=="0483", ATTR{idProduct}=="df11"' udev/50-zsa.rules
grep -q 'ATTR{idVendor}=="16c0", ATTR{idProduct}=="0478"' udev/50-zsa.rules

%files
%license LICENSE.md
%doc README.md
%{_bindir}/%{name}
%{_udevrulesdir}/50-zsa.rules

%changelog
%autochangelog
