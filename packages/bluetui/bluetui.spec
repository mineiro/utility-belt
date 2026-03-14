%global debug_package %{nil}

Name:           bluetui
Version:        0.8.1
Release:        %autorelease
Summary:        Terminal UI for managing Bluetooth on Linux

License:        GPL-3.0-only
URL:            https://github.com/pythops/bluetui
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
# Placeholder URL for a locally generated vendor tarball; SRPM helpers create
# the actual file before rpmbuild consumes it.
Source1:        https://example.invalid/%{name}-%{version}-vendor.tar.xz#/%{name}-%{version}-vendor.tar.xz
Patch0:         0001-disable-libdbus-sys-vendored-libdbus-build.patch

BuildRequires:  cargo
BuildRequires:  dbus-devel
BuildRequires:  pkgconf-pkg-config
BuildRequires:  rust >= 1.85
Requires:       bluez

# Vendored Rust crates are used to keep SRPM and COPR builds reproducible while
# the full dependency stack is not yet packaged in Fedora.
Provides:       bundled(crate(bluer)) = 0.17.4
Provides:       bundled(crate(clap)) = 4.5.54
Provides:       bundled(crate(crossterm)) = 0.29.0
Provides:       bundled(crate(dbus)) = 0.9.10
Provides:       bundled(crate(libdbus-sys)) = 0.2.7
Provides:       bundled(crate(ratatui)) = 0.30.0
Provides:       bundled(crate(tokio)) = 1.49.0

%description
Bluetui is a text user interface for managing Bluetooth adapters and devices on
Linux. It talks to BlueZ over D-Bus to scan, pair, connect, trust, and rename
devices from a terminal session.

%prep
%autosetup -p1
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
cargo build --release --frozen

%install
install -Dpm0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}

%check
./target/release/%{name} --version | grep -q "%{name} %{version}"

%files
%license LICENSE
%doc Readme.md
%doc Release.md
%{_bindir}/%{name}

%changelog
%autochangelog
