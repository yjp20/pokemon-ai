#!/usr/bin/env python3

# pylint: disable-all

import io
import os
import sys
from shutil import rmtree
from setuptools import find_packages, setup, Command

NAME = 'pokemon-dl'
DESCRIPTION = 'pokemon-dl that works with the showdown server with batteries included.'
URL = 'https://github.com/yjp20/pokemon-dl'
EMAIL = 'youngjinpark20@gmail.com'
AUTHOR = 'Young Jin Park'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.0.1'
REQUIRED = [ 'requests', 'websocket' ]
EXTRAS = { }

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ]
)
