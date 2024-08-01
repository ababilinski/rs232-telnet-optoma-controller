from __future__ import annotations

from cx_Freeze import Executable, setup
import os
import sys
try:
    from cx_Freeze.hooks import get_qt_plugins_paths
except ImportError:
    get_qt_plugins_paths = None
sys.path.append('scripts')

include_files = ["scripts/telnet_worker.py", "scripts/validation_utils.py", "scripts/commands.py"]
if get_qt_plugins_paths:
    # Inclusion of extra plugins (since cx_Freeze 6.8b2)
    # cx_Freeze automatically imports the following plugins depending on the
    # module used, but suppose we need the following:
    include_files += get_qt_plugins_paths("PyQt5", "multimedia")

build_exe_options = {
    # exclude packages that are not really needed
    "excludes": ["tkinter", "unittest", "email", "http", "xml", "pydoc"],
    "includes": ["commands", "telnet_worker", "validation_utils"],
    "include_files": include_files,
}

executables = [Executable("scripts/main.py", target_name="Telnet Optoma Controller.exe", base="gui", icon="data/icon", shortcut_name="Telnet Optoma Controller", copyright="© 2024 Adrian Babilinski. All rights reserved.")]

# Base set to "Win32GUI" to avoid the console window
base = None
if sys.platform == 'win64':
    base = 'Win64GUI'
elif sys.platform == 'win32':
    base = 'Win32GUI'

setup(
    name="Telnet Optoma Controller",
    version="1.0.0",
    author="Adrian Babilinski",
    license="Apache-2.0",
    description="Controls Optoma ZU725TST projectors using RS232 codes and Telnet.",
    options={"build_exe": build_exe_options},
    executables=executables
)
