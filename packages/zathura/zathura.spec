Name:           zathura
Version:        2026.03.27
Release:        %autorelease -b 2
Summary:        A lightweight document viewer

License:        Zlib
URL:            https://pwmt.org/projects/%{name}/
Source0:        %{url}/download/%{name}-%{version}.tar.xz

BuildRequires:  appstream
BuildRequires:  bash-completion
BuildRequires:  cairo-devel
BuildRequires:  desktop-file-utils
BuildRequires:  file-devel
BuildRequires:  fish
BuildRequires:  gcc
BuildRequires:  gettext
BuildRequires:  girara-devel >= 2026.02.04
BuildRequires:  glib2-devel >= 2.76
BuildRequires:  gtk3-devel >= 3.24
BuildRequires:  intltool
BuildRequires:  librsvg2-tools
BuildRequires:  libseccomp-devel
BuildRequires:  meson >= 1.5
BuildRequires:  pkgconfig(check) >= 0.11
BuildRequires:  pkgconfig(json-glib-1.0)
BuildRequires:  python3-sphinx
BuildRequires:  sqlite-devel >= 3.6.23
BuildRequires:  texlive-lib-devel
BuildRequires:  weston
BuildRequires:  xorg-x11-server-Xvfb
BuildRequires:  zsh

Suggests:       zathura-cb
Suggests:       zathura-djvu
Suggests:       zathura-pdf-poppler
Suggests:       zathura-ps
Suggests:       zathura-bash-completion
Suggests:       zathura-fish-completion
Suggests:       zathura-zsh-completion

%description
Zathura is a highly customizable and functional document viewer. It provides a
minimalistic and space saving interface as well as an easy usage model that
mainly focuses on keyboard interaction.

Zathura requires plugins to support document formats. For instance:
* zathura-pdf-poppler to open PDF files,
* zathura-ps to open PostScript files,
* zathura-djvu to open DjVu files, or
* zathura-cb to open comic book files.

All of these are available as separate packages in Fedora. A
zathura-plugins-all package is available should you want to install all
available plugins.

%package devel
Summary:        Development files for zathura
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       pkgconfig

%description devel
Libraries and header files for developing applications against zathura's plugin
API.

%package plugins-all
Summary:        Zathura plugins meta-package
Requires:       zathura-cb
Requires:       zathura-djvu
Requires:       zathura-pdf-poppler
Requires:       zathura-ps

%description plugins-all
This package installs all available Zathura plugins.

%package bash-completion
Summary:        Bash completion for zathura
BuildArch:      noarch
Requires:       bash-completion
Requires:       %{name} = %{version}-%{release}

%description bash-completion
This package provides bash completion support for zathura.

%package fish-completion
Summary:        Fish completion for zathura
BuildArch:      noarch
Requires:       fish
Requires:       %{name} = %{version}-%{release}

%description fish-completion
This package provides fish completion support for zathura.

%package zsh-completion
Summary:        Zsh completion for zathura
BuildArch:      noarch
Requires:       zsh
Requires:       %{name} = %{version}-%{release}

%description zsh-completion
This package provides zsh completion support for zathura.

%prep
%autosetup

%build
%meson \
    -Dconvert-icon=enabled \
    -Dlandlock=auto \
    -Dmanpages=enabled \
    -Dseccomp=enabled \
    -Dsynctex=enabled \
    -Dtests=enabled
%meson_build

%install
%meson_install
appstreamcli validate --no-net %{buildroot}%{_datadir}/metainfo/org.pwmt.zathura.metainfo.xml
desktop-file-validate %{buildroot}%{_datadir}/applications/org.pwmt.zathura.desktop
%find_lang org.pwmt.zathura

%check
%meson_test validate-desktop validate-appdata document types utils xvfb_session xvfb_config xvfb_setting weston_session weston_config weston_setting

%files -f org.pwmt.zathura.lang
%license LICENSE
%doc README.md
%{_bindir}/zathura
%{_bindir}/zathura-sandbox
%{_mandir}/man1/zathura.1*
%{_mandir}/man1/zathura-sandbox.1*
%{_mandir}/man5/zathurarc.5*
%{_datadir}/applications/org.pwmt.zathura.desktop
%{_datadir}/dbus-1/interfaces/org.pwmt.zathura.xml
%{_datadir}/icons/hicolor/*/apps/org.pwmt.zathura.png
%{_datadir}/icons/hicolor/*/apps/org.pwmt.zathura.svg
%{_datadir}/metainfo/org.pwmt.zathura.metainfo.xml

%files devel
%{_includedir}/zathura
%{_libdir}/pkgconfig/zathura.pc

%files plugins-all

%files bash-completion
%{_datadir}/bash-completion/completions/zathura

%files fish-completion
%{_datadir}/fish/vendor_completions.d/zathura.fish

%files zsh-completion
%{_datadir}/zsh/site-functions/_zathura

%changelog
%autochangelog
