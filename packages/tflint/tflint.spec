%global debug_package %{nil}

Name:           tflint
Version:        0.62.0
Release:        %autorelease
Summary:        Pluggable Terraform linter

License:        MPL-2.0 AND BUSL-1.1 AND BSD-3-Clause
URL:            https://github.com/terraform-linters/tflint
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
# Placeholder URL for a locally generated vendor tarball; SRPM helpers create
# the actual file before rpmbuild consumes it.
Source1:        https://example.invalid/%{name}-%{version}-vendor.tar.xz#/%{name}-%{version}-vendor.tar.xz

BuildRequires:  golang >= 1.26.2

%description
TFLint is a pluggable linter for Terraform code. It can validate Terraform
configurations, detect errors and anti-patterns, and integrate cloud-provider
rulesets through plugins.

%prep
%autosetup -p1
tar -xJf %{SOURCE1}

%build
export CGO_ENABLED=0
go build \
  -buildmode=pie \
  -compiler gc \
  -mod=vendor \
  -buildvcs=false \
  -trimpath \
  -o tflint-bin .

%install
install -Dpm0755 tflint-bin %{buildroot}%{_bindir}/%{name}

%check
./tflint-bin --version | grep -q "%{version}"

%files
%license LICENSE
%license LICENSE-BUSL
%license terraform/ipaddr/LICENSE
%{_bindir}/%{name}

%changelog
%autochangelog
