#!/usr/bin/env python

from setuptools import setup, find_packages

__version__ = "0.0.1"

setup(
    name='marstr-msal-extensions',
    version=__version__,
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
