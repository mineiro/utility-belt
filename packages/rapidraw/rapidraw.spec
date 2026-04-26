Name:           rapidraw
Version:        1.5.4
Release:        %autorelease
Summary:        GPU-accelerated RAW image editor

License:        AGPL-3.0-only
URL:            https://github.com/CyberTimon/RapidRAW
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
# Placeholder URLs for locally generated vendor tarballs. SRPM helpers create
# the actual files before rpmbuild consumes them.
Source1:        https://example.invalid/%{name}-%{version}-vendor.tar.xz#/%{name}-%{version}-vendor.tar.xz
Source2:        https://example.invalid/%{name}-%{version}-node-cache.tar.xz#/%{name}-%{version}-node-cache.tar.xz
Patch0:         0001-use-system-onnxruntime-on-fedora.patch
Patch1:         0002-use-system-libwebp-on-fedora.patch

BuildRequires:  cargo
BuildRequires:  desktop-file-utils
BuildRequires:  gcc-c++
BuildRequires:  glib2-devel
BuildRequires:  gtk3-devel
BuildRequires:  javascriptcoregtk4.1-devel
BuildRequires:  libayatana-appindicator-gtk3-devel
BuildRequires:  librsvg2-devel
BuildRequires:  nodejs >= 22
BuildRequires:  /usr/bin/npm
BuildRequires:  openssl-devel
BuildRequires:  pkgconf-pkg-config
BuildRequires:  pkgconfig(libsharpyuv)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(libwebpdemux)
BuildRequires:  pkgconfig(libwebpmux)
BuildRequires:  rust >= 1.94
BuildRequires:  webkit2gtk4.1-devel

Requires:       onnxruntime%{?_isa}

ExclusiveArch:  aarch64 x86_64

%description
RapidRAW is a modern RAW image editor built with a Tauri frontend and a Rust
processing backend. It provides non-destructive editing, GPU-accelerated
rendering, AI-assisted masking and tagging, and support for a wide range of RAW
camera formats.

%prep
%autosetup -n RapidRAW-%{version} -N
mkdir -p src-tauri/.cargo
cat > src-tauri/.cargo/config.toml <<'EOF'
[source.crates-io]
replace-with = "vendored-sources"

[source."git+https://github.com/CyberTimon/RapidRAW-DngLab.git"]
git = "https://github.com/CyberTimon/RapidRAW-DngLab.git"
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF
tar -C src-tauri -xJf %{SOURCE1}
tar -xJf %{SOURCE2}
%autopatch -p1
# Keep Cargo.lock in sync with the patched libwebp-sys build dependency.
sed -i '/^name = "libwebp-sys"$/,/^\]$/ { / "glob",/a\ "pkg-config",
}' src-tauri/Cargo.lock
# Keep Cargo's vendor integrity metadata in sync with the patched libwebp-sys crate.
sed -i \
  -e 's#"Cargo.toml":"[^"]*"#"Cargo.toml":"c5efb6ecb15c52f2fc20418cb5b7aedad2f22185fc5afc6eac3e94ca3f286dd3"#' \
  -e 's#"build.rs":"[^"]*"#"build.rs":"17444c540ff8fdbb86ac714be45bb4152086e85484f4930dc17b0ffb9755b31f"#' \
  src-tauri/vendor/libwebp-sys/.cargo-checksum.json
find src-tauri/vendor -type f -exec chmod a-x {} +

%build
%set_build_flags
export CARGO_HOME="$PWD/.cargo-home"
export CARGO_NET_OFFLINE=true
export RUSTFLAGS="${RUSTFLAGS:-%{build_rustflags}}"
# Upstream enables full LTO in the release profile, which can leave COPR
# builders stuck in a very long final link step. Use Fedora's standard Rust
# flags and let RPM handle stripping/debug info instead.
export CARGO_PROFILE_RELEASE_LTO=false
export CARGO_PROFILE_RELEASE_STRIP=none
export ORT_STRATEGY=system
export RAPIDRAW_SYSTEM_ORT_LIBDIR=%{_libdir}
export npm_config_cache="$PWD/npm-cache"
export npm_config_offline=true
export npm_config_audit=false
export npm_config_fund=false
export npm_config_update_notifier=false
export npm_config_legacy_peer_deps=true
npm ci --offline --legacy-peer-deps
npm run tauri build -- --no-bundle

%install
install -Dpm0755 src-tauri/target/release/RapidRAW %{buildroot}%{_bindir}/RapidRAW

install -d %{buildroot}%{_prefix}/lib/RapidRAW
cp -a src-tauri/lensfun_db %{buildroot}%{_prefix}/lib/RapidRAW/
cp -a src-tauri/resources %{buildroot}%{_prefix}/lib/RapidRAW/
find %{buildroot}%{_prefix}/lib/RapidRAW/resources -maxdepth 1 -name 'libonnxruntime*' -delete

desktop-file-install \
  --dir=%{buildroot}%{_datadir}/applications \
  --set-key=Icon \
  --set-value=io.github.CyberTimon.RapidRAW \
  --set-key=StartupWMClass \
  --set-value=RapidRAW \
  data/io.github.CyberTimon.RapidRAW.desktop

install -Dpm0644 data/io.github.CyberTimon.RapidRAW.metainfo.xml \
  %{buildroot}%{_metainfodir}/io.github.CyberTimon.RapidRAW.metainfo.xml

install -Dpm0644 src-tauri/icons/32x32.png \
  %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/io.github.CyberTimon.RapidRAW.png
install -Dpm0644 src-tauri/icons/128x128.png \
  %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/io.github.CyberTimon.RapidRAW.png
install -Dpm0644 src-tauri/icons/128x128@2x.png \
  %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/io.github.CyberTimon.RapidRAW.png
install -Dpm0644 src-tauri/icons/icon.png \
  %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/io.github.CyberTimon.RapidRAW.png

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/io.github.CyberTimon.RapidRAW.desktop
test -x src-tauri/target/release/RapidRAW

%files
%license LICENSE
%doc README.md
%{_bindir}/RapidRAW
%{_prefix}/lib/RapidRAW
%{_datadir}/applications/io.github.CyberTimon.RapidRAW.desktop
%{_datadir}/icons/hicolor/32x32/apps/io.github.CyberTimon.RapidRAW.png
%{_datadir}/icons/hicolor/128x128/apps/io.github.CyberTimon.RapidRAW.png
%{_datadir}/icons/hicolor/256x256/apps/io.github.CyberTimon.RapidRAW.png
%{_datadir}/icons/hicolor/512x512/apps/io.github.CyberTimon.RapidRAW.png
%{_metainfodir}/io.github.CyberTimon.RapidRAW.metainfo.xml

%changelog
%autochangelog
