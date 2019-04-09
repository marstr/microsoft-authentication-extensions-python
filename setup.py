#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='msal-extensions',
    packages=find_packages(exclude=[
        "tests",
    ]),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
    ],
)
