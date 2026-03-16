Name:           zathura-cb
Version:        2026.02.03
Release:        %autorelease
Summary:        Comic book support for zathura

License:        Zlib
URL:            https://pwmt.org/projects/%{name}
Source0:        %{url}/download/%{name}-%{version}.tar.xz

BuildRequires:  appstream
BuildRequires:  cairo-devel
BuildRequires:  desktop-file-utils
BuildRequires:  gcc
BuildRequires:  girara-devel >= 2026.02.04
BuildRequires:  glib2-devel
BuildRequires:  libarchive-devel
BuildRequires:  meson >= 0.61
BuildRequires:  zathura-devel >= 2026.01.30

Requires:       zathura >= 2026.01.30

%description
The zathura-cb plugin adds comic book archive support to zathura.

%prep
%autosetup

%build
%meson
%meson_build

%install
%meson_install
desktop-file-validate %{buildroot}%{_datadir}/applications/org.pwmt.zathura-cb.desktop
appstreamcli validate --no-net %{buildroot}%{_datadir}/metainfo/org.pwmt.zathura-cb.metainfo.xml

%files
%license LICENSE
%doc AUTHORS README.md
%{_libdir}/zathura/libcb.so
%{_datadir}/applications/org.pwmt.zathura-cb.desktop
%{_datadir}/metainfo/org.pwmt.zathura-cb.metainfo.xml

%changelog
%autochangelog
