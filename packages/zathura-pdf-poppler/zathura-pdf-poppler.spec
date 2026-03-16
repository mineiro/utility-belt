Name:           zathura-pdf-poppler
Version:        2026.02.03
Release:        %autorelease
Summary:        PDF support for zathura via poppler

License:        Zlib
URL:            https://pwmt.org/projects/%{name}
Source0:        %{url}/download/%{name}-%{version}.tar.xz

BuildRequires:  appstream
BuildRequires:  desktop-file-utils
BuildRequires:  gcc
BuildRequires:  girara-devel >= 2026.02.04
BuildRequires:  glib2-devel
BuildRequires:  meson >= 0.61
BuildRequires:  poppler-glib-devel >= 21.12
BuildRequires:  zathura-devel >= 2026.01.30

Requires:       zathura >= 2026.01.30
Conflicts:      zathura-pdf-mupdf < %{version}

%description
The zathura-pdf-poppler plugin adds PDF support to zathura by using
the poppler rendering engine.

%prep
%autosetup

%build
%meson
%meson_build

%install
%meson_install
desktop-file-validate %{buildroot}%{_datadir}/applications/org.pwmt.zathura-pdf-poppler.desktop
appstreamcli validate --no-net %{buildroot}%{_datadir}/metainfo/org.pwmt.zathura-pdf-poppler.metainfo.xml

%pre
[ -L %{_libdir}/zathura/pdf.so ] || rm -f %{_libdir}/zathura/pdf.so

%files
%license LICENSE
%doc AUTHORS README.md
%{_libdir}/zathura/libpdf-poppler.so
%{_datadir}/applications/org.pwmt.zathura-pdf-poppler.desktop
%{_datadir}/metainfo/org.pwmt.zathura-pdf-poppler.metainfo.xml

%changelog
%autochangelog
