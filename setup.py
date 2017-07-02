import os

from setuptools import find_packages
from setuptools import setup


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
        'NSHumanReadableCopyright': ('Copyright (c) 2017 Eric Brown. '
                                     'All rights reserved.'),
    },
    'packages': ['rumps'],
}


setup(
    name='SlackStatus',
    version='1.0',
    app=['main.py'],
    author='Eric Brown',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    packages=find_packages(),
    setup_requires=[
        'py2app',
        'pyobjc-framework-CalendarStore',
        'pyobjc-framework-CoreWLAN',
        'pyobjc-framework-Quartz',
    ],
)
