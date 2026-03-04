Name:           try-cli
Version:        1.5.3
Release:        %autorelease
Summary:        Ephemeral workspace manager with fuzzy directory search

License:        MIT
URL:            https://github.com/tobi/try-cli
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  make
Requires:       bash

%description
try is a fast interactive command-line tool for managing short-lived
development workspaces. It provides fuzzy matching, recency-aware ranking,
and automatic date-prefixed directory creation to quickly revisit or create
experiments.

%prep
%autosetup -p1

%build
%set_build_flags
%make_build

%install
install -Dpm0755 dist/try %{buildroot}%{_bindir}/try

%check
./dist/try --version | grep -q "try %{version}"

%files
%license src/libs/acutest.h
%doc README.md
%{_bindir}/try

%changelog
%autochangelog
