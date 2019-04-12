#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='msal-extensions',
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
    ],
    extras_require={
        'dev': [
            'pytest',
        ]
    },
)
