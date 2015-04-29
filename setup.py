#! /usr/bin/python

from setuptools.command import easy_install
from setuptools import setup, find_packages
import shutil
import os.path
import sys
import hashlib

setup(
    name = "kmltrack",
    description = "kmltrack converts a track (a series of lat/lon/timestamp and optional measurement values) into a kml file.",
    keywords = "kml",
    install_requires = ["python-dateutil"],
    extras_require = {
        'cli':  ["click>=3.3"],
        'msgpack':  ["msgpack-python>=0.4.2"],
        'test': ["elementtree>=1.2.6", "nose", "coverage"]
    },
    version = "0.0.6",
    author = "Egil Moeller",
    author_email = "egil@skytruth.org",
    license = "GPL",
    url = "https://github.com/SkyTruth/kmltrack",
    packages=[
        'kmltrack',
    ],
    entry_points='''
        [console_scripts]
        kmltrack=kmltrack.cli:main
    '''
)
