Name:           zathura-ps
Version:        2026.02.03
Release:        %autorelease
Summary:        PostScript support for zathura via libspectre

License:        Zlib
URL:            https://pwmt.org/projects/%{name}
Source0:        %{url}/download/%{name}-%{version}.tar.xz

BuildRequires:  appstream
BuildRequires:  cairo-devel
BuildRequires:  desktop-file-utils
BuildRequires:  gcc
BuildRequires:  girara-devel >= 2026.02.04
BuildRequires:  glib2-devel
BuildRequires:  libspectre-devel
BuildRequires:  meson >= 0.61
BuildRequires:  zathura-devel >= 2026.01.30

Requires:       zathura >= 2026.01.30

%description
The zathura-ps plugin adds PostScript support to zathura by
using the libspectre library.

%prep
%autosetup

%build
%meson
%meson_build

%install
%meson_install
desktop-file-validate %{buildroot}%{_datadir}/applications/org.pwmt.zathura-ps.desktop
appstreamcli validate --no-net %{buildroot}%{_datadir}/metainfo/org.pwmt.zathura-ps.metainfo.xml

%files
%license LICENSE
%doc AUTHORS
%{_libdir}/zathura/libps.so
%{_datadir}/applications/org.pwmt.zathura-ps.desktop
%{_datadir}/metainfo/org.pwmt.zathura-ps.metainfo.xml

%changelog
%autochangelog
