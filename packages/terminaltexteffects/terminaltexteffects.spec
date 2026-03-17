%global pypi_name terminaltexteffects

Name:           terminaltexteffects
Version:        0.14.2
Release:        %autorelease
Summary:        Terminal visual effects engine for animated text output

License:        MIT
URL:            https://github.com/ChrisBuilds/terminaltexteffects
Source0:        https://files.pythonhosted.org/packages/source/t/%{pypi_name}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel

%generate_buildrequires
%pyproject_buildrequires

%description
TerminalTextEffects is a Python terminal visual effects engine that can be used
as a command-line application or as a library. It provides animated text
effects for piped terminal input and reusable effect primitives for Python
programs.

%prep
%autosetup -n %{pypi_name}-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{pypi_name}

%check
# The upstream sdist excludes tests, so keep validation to installed CLI smoke checks.
PYTHONNOUSERSITE=1 \
PYTHONPATH=%{buildroot}%{python3_sitelib} \
PATH=%{buildroot}%{_bindir}:$PATH \
tte --version | grep -q "TerminalTextEffects %{version}"
PYTHONNOUSERSITE=1 \
PYTHONPATH=%{buildroot}%{python3_sitelib} \
PATH=%{buildroot}%{_bindir}:$PATH \
terminaltexteffects --version | grep -q "TerminalTextEffects %{version}"

%files -f %{pyproject_files}
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/tte
%{_bindir}/terminaltexteffects

%changelog
%autochangelog
