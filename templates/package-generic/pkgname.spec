# Starter spec template (generic C/C++ style). Update build/install macros as needed.

Name:           pkgname
Version:        0.0.0
Release:        %autorelease
Summary:        TODO summary

License:        TODO
URL:            https://example.invalid
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make

%description
TODO description.

%prep
%autosetup -p1

%build
%configure
%make_build

%install
%make_install

%files
# TODO: list files

%changelog
%autochangelog
