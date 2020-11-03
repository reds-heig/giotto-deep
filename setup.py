#! /usr/bin/env python
"""Toolbox for Machine Learning using Topological Data Analysis."""

import os
import codecs
import re
import sys
import platform
import subprocess

from distutils.version import LooseVersion
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext


version_file = os.path.join("gdeep", "_version.py")
with open(version_file) as f:
    exec(f.read())

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

DISTNAME = "giotto-deep"
DESCRIPTION = "Toolbox for Deep Learning and Topological Data Analysis."
with codecs.open("README.md", encoding="utf-8-sig") as f:
    LONG_DESCRIPTION = f.read()
LONG_DESCRIPTION_TYPE = "text/x-md"
MAINTAINER = "Matteo Caorsi"
MAINTAINER_EMAIL = "maintainers@giotto.ai"
URL = "https://github.com/giotto-ai/giotto-deep"
LICENSE = "GNU AGPLv3"
VERSION = __version__  # noqa
DOWNLOAD_URL = "https://github.com/giotto-ai/giotto-deep/tarball/v"+VERSION
CLASSIFIERS = ["Intended Audience :: Science/Research",
               "Intended Audience :: Developers",
               "License :: OSI Approved",
               "Programming Language :: C++",
               "Programming Language :: Python",
               "Topic :: Software Development",
               "Topic :: Scientific/Engineering",
               "Operating System :: Microsoft :: Windows",
               "Operating System :: POSIX",
               "Operating System :: Unix",
               "Operating System :: MacOS",
               "Programming Language :: Python :: 3.6",
               "Programming Language :: Python :: 3.7",
               "Programming Language :: Python :: 3.8"]
KEYWORDS = "deep learning, topological data analysis, persistent " \
           "homology, persistence diagrams"
INSTALL_REQUIRES = requirements
EXTRAS_REQUIRE = {"tests": ["pytest",
                            "flake8"],
                  "doc": ["openml",
                          "sphinx",
                          "nbconvert",
                          "sphinx-issues",
                          "sphinx_rtd_theme",
                          "numpydoc"],
                  "examples": ["jupyter",
                               "pandas",
                               "openml",
                               "plotly"]}

setup(name=DISTNAME,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      description=DESCRIPTION,
      license=LICENSE,
      url=URL,
      version=VERSION,
      download_url=DOWNLOAD_URL,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESCRIPTION_TYPE,
      zip_safe=False,
      classifiers=CLASSIFIERS,
      packages=find_packages(),
      keywords=KEYWORDS,
      install_requires=INSTALL_REQUIRES,
      extras_require=EXTRAS_REQUIRE)
