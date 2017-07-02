import os
from setuptools import setup


APP = ['status.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': os.path.join('icons', 'Slack_Icon.icns'),
    'plist': {
        'CFBundleIdentifier': 'ericwb.slack-status-bar',
        'CFBundleName': 'Slack Status',
        'CFBundleShortVersionString': '1.0',
        'CFBundleVersion': '1',
        'LSMinimumSystemVersion': '10.12',
        'LSUIElement': True,
        'NSHumanReadableCopyright': ('Copyright (c) 2017 Eric Brown. All '
                                     'rights reserved.'),
    },
    'packages': ['rumps'],
}


setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app', 'PyYAML', 'requests'],
)
