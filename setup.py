#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

VERSION = '1.0.0'

with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()
with open("readme.rst", 'r') as f:
    long_description = f.read()

setup(
    name="pushjet",
    version=VERSION,
    install_requires=requirements,
    packages=['pushjet'],
    author="Samuel Messner",
    author_email="powpowd@gmail.com",
    url="https://github.com/obskyr/pushjet-py",
    download_url="https://github.com/obskyr/pushjet-py/tarball/v" + VERSION,
    description="A Python API for Pushjet. Send notifications to your phone from Python scripts!",
    long_description=long_description,
    license="MIT",
    keywords="pushjet notifications android phone api rest",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"
    ]
)
