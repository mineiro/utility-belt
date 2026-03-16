Name:           zathura-djvu
Version:        2026.02.03
Release:        %autorelease
Summary:        DjVu support for zathura

License:        Zlib
URL:            https://pwmt.org/projects/%{name}
Source0:        %{url}/download/%{name}-%{version}.tar.xz

BuildRequires:  appstream
BuildRequires:  cairo-devel
BuildRequires:  desktop-file-utils
BuildRequires:  djvulibre-devel
BuildRequires:  gcc
BuildRequires:  girara-devel >= 2026.02.04
BuildRequires:  glib2-devel
BuildRequires:  meson >= 0.61
BuildRequires:  zathura-devel >= 2026.01.30

Requires:       zathura >= 2026.01.30

%description
The zathura-djvu plugin adds DjVu support to zathura by
using the djvulibre library.

%prep
%autosetup

%build
%meson
%meson_build

%install
%meson_install
desktop-file-validate %{buildroot}%{_datadir}/applications/org.pwmt.zathura-djvu.desktop
appstreamcli validate --no-net %{buildroot}%{_datadir}/metainfo/org.pwmt.zathura-djvu.metainfo.xml

%files
%license LICENSE
%doc AUTHORS
%{_libdir}/zathura/libdjvu.so
%{_datadir}/applications/org.pwmt.zathura-djvu.desktop
%{_datadir}/metainfo/org.pwmt.zathura-djvu.metainfo.xml

%changelog
%autochangelog
