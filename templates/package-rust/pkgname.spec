# Starter spec template (Rust CLI, vendored). Update metadata and crate list.

Name:           pkgname
Version:        0.0.0
Release:        %autorelease
Summary:        TODO summary

License:        TODO
URL:            https://example.invalid
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-vendor.tar.xz

BuildRequires:  cargo-rpm-macros >= 26
BuildRequires:  rust-packaging

# TODO: replace with concrete bundled crate virtual provides if required by policy.
Provides:       bundled(crate(example)) = 0

%description
TODO description.

%prep
%autosetup -p1
%cargo_prep -v vendor

%build
%cargo_build

%install
%cargo_install

%files
%{_bindir}/%{name}

%changelog
%autochangelog
