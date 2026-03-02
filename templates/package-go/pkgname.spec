# Starter spec template (Go CLI). Adjust build flags and file list.

Name:           pkgname
Version:        0.0.0
Release:        %autorelease
Summary:        TODO summary

License:        TODO
URL:            https://example.invalid
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  golang

%description
TODO description.

%prep
%autosetup -p1

%build
# Use upstream module mode by default. Switch to -mod=vendor if you ship Source1 vendor tarball.
go build \
  -buildmode=pie \
  -compiler gc \
  -buildvcs=false \
  -ldflags "-linkmode external -extldflags '%{__global_ldflags}'" \
  -o %{name} .

%install
install -Dpm0755 %{name} %{buildroot}%{_bindir}/%{name}

%files
%{_bindir}/%{name}

%changelog
%autochangelog
