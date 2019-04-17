#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='msal_extensions',
    package_dir={
        '': 'src',
    },
    packages=find_packages(
        where="./src",
    ),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
    ],
    install_requires=[
        'msal~=0.3.0',
        'psutil~=5.6',
        'portalocker~=1.4',
    ],
    extras_require={
        'dev': [
            'pytest',
        ]
    },
)
