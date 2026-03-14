Name:           impala
Version:        0.7.4
Release:        %autorelease
Summary:        Terminal UI for managing Wi-Fi with the Intel Wireless Daemon

License:        GPL-3.0-only
URL:            https://github.com/pythops/impala
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
# Placeholder URL for a locally generated vendor tarball; SRPM helpers create
# the actual file before rpmbuild consumes it.
Source1:        https://example.invalid/%{name}-%{version}-vendor.tar.xz#/%{name}-%{version}-vendor.tar.xz

BuildRequires:  cargo
BuildRequires:  help2man
BuildRequires:  rust >= 1.85
Requires:       iwd

# Vendored Rust crates are used to keep SRPM and COPR builds reproducible while
# the dependency stack is not yet packaged in Fedora.
Provides:       bundled(crate(iwdrs)) = 0.2.6
Provides:       bundled(crate(zbus)) = 5.13.2
Provides:       bundled(crate(chrono)) = 0.4.43
Provides:       bundled(crate(env_logger)) = 0.11.9
Provides:       bundled(crate(qrcode)) = 0.14.1
Provides:       bundled(crate(tui-qrcode)) = 0.2.2
Provides:       bundled(crate(ratatui)) = 0.30.0
Provides:       bundled(crate(tokio)) = 1.49.0
Provides:       bundled(crate(clap)) = 4.5.58
Provides:       bundled(crate(crossterm)) = 0.29.0

%description
Impala is a text user interface for managing Wi-Fi on Linux through the Intel
Wireless Daemon. It supports station and access point modes, hidden networks,
QR code sharing, and WPA Enterprise network configuration from a terminal
session.

%prep
%autosetup
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
NO_COLOR=1 help2man --no-info \
  --name "%{summary}" \
  ./target/release/%{name} > %{name}.1

%install
install -Dpm0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}
install -Dpm0644 %{name}.1 %{buildroot}%{_mandir}/man1/%{name}.1

%check
./target/release/%{name} --version | grep -q "%{name} %{version}"

%files
%license LICENSE
%doc Readme.md
%doc Release.md
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*

%changelog
%autochangelog
