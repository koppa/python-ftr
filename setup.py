#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Python Five-Filters setup.py. """

import sys

from setuptools import setup, find_packages

if '.' in sys.path:
    sys.path.remove('.')

setup(
    name="ftr",
    version='0.0',
    author="Olivier Cortès",
    author_email="contact@oliviercortes.com",
    description="HTML Article cleaner / extractor, Five-Filters compatible.",
    long_description=open('README.md').read(),
    url="https://github.com/1flow/python-ftr",
    packages=find_packages(),
    include_package_data=True,
    dependency_links=[
        'https://github.com/Karmak23/humanize/tarball/master#egg=humanize',
    ],
    install_requires=[
        # 'html5lib',
        'pytidylib',
        'lxml',
        'ordered-set',
        'readability-lxml',
        'requests',
    ],
    extras_require={
        'cache':  ['cacheops'],
    },
    keywords=(
        'parsing',
        'websites',
        'articles',
    ),
    license='AGPLv3',
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",  # NOQA
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Text Processing :: Filters",
    ],
)
