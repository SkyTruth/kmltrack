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
        'cli':  ["click"]
    },
    version = "0.0.3",
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
