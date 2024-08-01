from setuptools import setup

APP = ['scripts/main.py']
APP_NAME = 'Telnet Optoma Controller'
DATA_FILES = []
OPTIONS = {
    'iconfile': 'data/icon.icns',
    'argv_emulation': False,
    'includes': ['PyQt5.QtCore', 'telnetlib', 'PyQt5','os','commands', 'telnet_worker', 'validation_utils'],  # List all packages needed
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'LSApplicationCategoryType':"public.app-category.utilities",
        'CFBundleIdentifier': "com.babilinapps.osx.telnetController",
        'CFBundleVersion': "2.0.0",
        'CFBundleShortVersionString': "2.0.0",
        'NSHumanReadableCopyright': u"Copyright © 2024, Adrian Babilinski, All Rights Reserved"
    }
}

setup(
    app=APP,
    name=APP_NAME,
    version='2.0.0',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
