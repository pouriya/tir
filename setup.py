#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import codecs
from setuptools import setup, find_packages


cwd = os.path.abspath(os.path.dirname(__file__))
metadata = codecs.open(os.path.join(cwd, 'tir', '__init__.py'), 'rb', 'utf-8').read()

def extract_metaitem(meta):
    meta_match = re.search(r"""^__{meta}__\s+=\s+['\"]([^'\"]*)['\"]""".format(meta=meta)
                          ,metadata
                          ,re.MULTILINE)
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError('Unable to find __{meta}__ string.'.format(meta=meta))

setup(name='tir'
     ,version=extract_metaitem('version')
     ,description=extract_metaitem('description')
     ,author=extract_metaitem('author')
     ,author_email=extract_metaitem('email')
     ,maintainer=extract_metaitem('author')
     ,maintainer_email=extract_metaitem('email')
     ,platforms=['Any']
     ,packages=find_packages()
     ,install_requires=['requests', 'lxml']
     ,setup_requires=['pytest-runner'])
