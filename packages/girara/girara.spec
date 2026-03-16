Name:           girara
Version:        2026.02.04
Release:        %autorelease -b 2
Summary:        Common utility library used by zathura

License:        Zlib
URL:            https://pwmt.org/projects/%{name}/
Source0:        %{url}/download/%{name}-%{version}.tar.xz

BuildRequires:  gcc
BuildRequires:  gettext
BuildRequires:  glib2-devel >= 2.72
BuildRequires:  meson >= 1.5
BuildRequires:  pkgconfig(check) >= 0.11

%description
Girara is a small utility library that provides common functionality used by
zathura and related applications.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and header files for developing
applications that use %{name}.

%prep
%autosetup

%build
%meson -Ddocs=disabled -Dtests=enabled
%meson_build

%install
%meson_install

%check
%meson_test

%files
%license LICENSE
%doc AUTHORS README.md
%{_libdir}/lib%{name}.so.5{,.*}

%files devel
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*.h
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/lib%{name}.so

%changelog
%autochangelog
