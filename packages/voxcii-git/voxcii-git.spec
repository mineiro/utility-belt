%global upstream_name voxcii
%global commit c7ff4ee02db3498fdf3da085a270fabc60fdd49c
%global shortcommit c7ff4ee
%global snapshot_date 20260306

Name:           voxcii-git
Version:        %{snapshot_date}git%{shortcommit}
Release:        %autorelease
Summary:        Terminal-based ASCII 3D model viewer

License:        MIT
URL:            https://github.com/ashish0kumar/voxcii
Source0:        %{url}/archive/%{commit}/%{upstream_name}-%{commit}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  ncurses-devel

Provides:       %{upstream_name} = %{version}-%{release}
Conflicts:      %{upstream_name}

%description
voxcii is a terminal-based ASCII 3D model viewer written in C++. It renders
OBJ and STL models with ASCII shading, a z-buffer for depth handling, and an
optional interactive mode for rotating models in the terminal.

This package tracks an upstream git snapshot because the project does not yet
publish tagged releases.

%prep
%autosetup -n %{upstream_name}-%{commit}

%build
%set_build_flags
%make_build \
    CXX="%{__cxx}" \
    CXXFLAGS="%{build_cxxflags} -std=c++17 -Wall" \
    LIBS="%{build_ldflags} -lncurses"

%install
install -Dpm0755 %{upstream_name} %{buildroot}%{_bindir}/%{upstream_name}
install -d %{buildroot}%{_datadir}/%{upstream_name}/models
install -pm0644 models/* %{buildroot}%{_datadir}/%{upstream_name}/models/

%check
set +e
./%{upstream_name} > usage.txt 2>&1
status=$?
set -e
test "${status}" -eq 1
grep -q "^Usage:" usage.txt

%files
%license LICENSE
%doc README.md
%{_bindir}/%{upstream_name}
%dir %{_datadir}/%{upstream_name}
%dir %{_datadir}/%{upstream_name}/models
%{_datadir}/%{upstream_name}/models/*

%changelog
%autochangelog
