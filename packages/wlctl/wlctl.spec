Name:           wlctl
Version:        0.1.5
Release:        %autorelease
Summary:        Terminal UI for managing Wi-Fi with NetworkManager

License:        GPL-3.0-only
URL:            https://github.com/aashish-thapa/wlctl
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
# Placeholder URL for a locally generated vendor tarball; SRPM helpers create
# the actual file before rpmbuild consumes it.
Source1:        https://example.invalid/%{name}-%{version}-vendor.tar.xz#/%{name}-%{version}-vendor.tar.xz

BuildRequires:  cargo
BuildRequires:  help2man
BuildRequires:  rust >= 1.85
Requires:       NetworkManager

# Keep wlctl's own debugsource content, but drop vendored crates right after
# find-debuginfo copies them into the buildroot. Some vendored Rust files start
# with inner attributes that Fedora's shebang BRP script misdetects.
%global _debugsource_vendor_dir %{buildroot}%{_prefix}/src/debug/%{name}-%{version}-%{release}.%{_arch}/vendor
%global _wlctl_orig_arch_install_post %{__arch_install_post}
%global __arch_install_post if [ -d "%{_debugsource_vendor_dir}" ]; then rm -rf "%{_debugsource_vendor_dir}"; fi ; %{_wlctl_orig_arch_install_post}

# Vendored Rust crates are used to keep SRPM and COPR builds reproducible while
# the dependency stack is not yet packaged in Fedora.
Provides:       bundled(crate(anyhow)) = 1.0.100
Provides:       bundled(crate(chrono)) = 0.4.42
Provides:       bundled(crate(clap)) = 4.5.53
Provides:       bundled(crate(crossterm)) = 0.29.0
Provides:       bundled(crate(dirs)) = 6.0.0
Provides:       bundled(crate(env_logger)) = 0.11.8
Provides:       bundled(crate(futures)) = 0.3.31
Provides:       bundled(crate(qrcode)) = 0.14.1
Provides:       bundled(crate(ratatui)) = 0.29.0
Provides:       bundled(crate(tokio)) = 1.48.0
Provides:       bundled(crate(toml)) = 0.9.8
Provides:       bundled(crate(tui-input)) = 0.14.0
Provides:       bundled(crate(tui-qrcode)) = 0.1.3
Provides:       bundled(crate(zbus)) = 5.12.0

%description
wlctl is a text user interface for managing Wi-Fi on Linux through
NetworkManager. It supports station and access point modes, hidden networks,
WPA Enterprise configuration, and QR code sharing from a terminal session.

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
%doc CHANGELOG.md
%doc Readme.md
%doc Release.md
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*

%changelog
%autochangelog
