Name:           keylight-control
Version:        1.2.0
Release:        %autorelease
Summary:        Qt desktop controller for Elgato Key Light devices

License:        GPL-3.0-only
URL:            https://github.com/sandwichfarm/keylight-control
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
# Upstream advertises GPL-3.0 but does not ship a license text in the release tarball.
Source1:        https://www.gnu.org/licenses/gpl-3.0.txt#/%{name}-%{version}-GPL-3.0.txt
Patch0:         0001-fix-fallback-event-loop-when-qasync-is-unavailable.patch

BuildArch:      noarch

BuildRequires:  desktop-file-utils
BuildRequires:  python3
BuildRequires:  python3-aiohttp
BuildRequires:  python3-pyside6
BuildRequires:  python3-zeroconf

Requires:       python3
Requires:       python3-aiohttp
Requires:       python3-pyside6
Requires:       python3-zeroconf
# qasync is optional upstream; the application falls back to a plain asyncio loop
# when it is unavailable, so it is not a hard Fedora dependency.

%description
keylight-control is a standalone Linux controller for Elgato Key Light
devices. It discovers compatible lights on the local network and provides a
Qt desktop UI for power, brightness, color temperature, and tray-based control.

%prep
%autosetup -p1

%build
# No build step needed for this pure-Python desktop application.

%check
python3 -m py_compile $(find src -type f -name '*.py' -print)
PYTHONPATH=src python3 - <<'PY'
import keylight_controller as app

app.__version__ = "%{version}"
assert app.__version__ == "%{version}"
PY
QT_QPA_PLATFORM=offscreen PYTHONPATH=src python3 - <<'PY'
import asyncio
import builtins
import sys

import keylight_controller as app
from PySide6.QtCore import QTimer

real_import = builtins.__import__


def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "qasync":
        raise ImportError("forced fallback for package test")
    return real_import(name, globals, locals, fromlist, level)


class DummySingleInstance:
    def __init__(self):
        self.socket = self

    def is_running(self):
        return False

    def setblocking(self, _value):
        return None

    def accept(self):
        raise BlockingIOError()

    def cleanup(self):
        return None


class DummyController:
    def show(self):
        QTimer.singleShot(0, lambda: asyncio.get_event_loop().stop())

    def raise_(self):
        return None

    def activateWindow(self):
        return None

    def quit_application(self):
        return None


builtins.__import__ = fake_import
app.SingleInstance = DummySingleInstance
app.KeyLightController = DummyController
sys.argv = ["keylight-controller"]

try:
    app.main()
finally:
    builtins.__import__ = real_import

print("fallback loop check: ok")
PY

%install
install -d %{buildroot}%{_datadir}/%{name}
install -d %{buildroot}%{_datadir}/applications
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_mandir}/man1
cp -a src %{buildroot}%{_datadir}/%{name}/

install -Dpm0644 %{SOURCE1} %{buildroot}%{_datadir}/licenses/%{name}/GPL-3.0.txt

# Private modules live under /usr/share and are launched through the wrapper.
sed -i '1{/^#!.*python3$/d;}' \
  %{buildroot}%{_datadir}/%{name}/src/config.py \
  %{buildroot}%{_datadir}/%{name}/src/keylight_controller.py

cat > %{buildroot}%{_bindir}/keylight-controller <<EOF
#!/usr/bin/python3
import sys

sys.path.insert(0, "%{_datadir}/%{name}/src")

import keylight_controller as app

app.__version__ = "%{version}"

if __name__ == "__main__":
    app.main()
EOF
chmod 0755 %{buildroot}%{_bindir}/keylight-controller

desktop-file-install \
  --dir=%{buildroot}%{_datadir}/applications \
  --set-key=Exec --set-value=keylight-controller \
  --remove-key=Path \
  keylight-controller.desktop

cat > %{buildroot}%{_mandir}/man1/keylight-controller.1 <<'EOF'
.TH KEYLIGHT-CONTROLLER 1
.SH NAME
keylight-controller \- desktop controller for Elgato Key Light devices
.SH SYNOPSIS
.B keylight-controller
[\fB\-\-version\fR]
[\fB\-\-debug\fR]
.SH DESCRIPTION
.B keylight-controller
discovers supported Elgato Key Light devices on the local network and opens a
Qt desktop interface for controlling power, brightness, and color temperature.
.SH OPTIONS
.TP
.B \-\-version
Print the packaged application version and exit.
.TP
.B \-\-debug
Enable debug output.
EOF

%files
%license %{_datadir}/licenses/%{name}/GPL-3.0.txt
%doc README.md
%doc CHANGELOG.md
%{_bindir}/keylight-controller
%{_mandir}/man1/keylight-controller.1*
%{_datadir}/%{name}
%{_datadir}/applications/keylight-controller.desktop

%changelog
%autochangelog
