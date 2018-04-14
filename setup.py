#!/usr/bin/python
from distutils.core import setup
from setuptools import find_packages

setup(
    setup_requires=[
        'pbr >= 1.9',
        'setuptools >= 17.1'
    ],
    pbr=True
)
