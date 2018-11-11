#!/usr/bin/env python3

import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

about = {}

with open(os.path.join(here, 'tir', '__version__.py'), mode='rt', encoding='utf-8') as f:
    exec(f.read(), about)

requires = [
        'requests',
        'lxml',
        ]

setup(
        name=about['__title__']
        version=about['__version__'],
        description=about['__desciption__'],
        author=about['__author__'],
        author_email=about['__author_email__'],
        url=about['__url__'],
        install_requires=requires,
        setup_requires=['pytest-runner'],
        packages=find_packages(),
 )
