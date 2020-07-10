# -*- coding: utf-8 -*-
"""
"""
from pathlib import Path

from setuptools import find_packages
from setuptools import setup

# Read the `__about__.py` file.
about = dict()
about_file = Path.cwd() / "src" / "reference_proj" / "__about__.py"
with open(about_file) as openf:
    exec(openf.read(), about)

INSTALL_REQUIRES = []
CLASSIFIERS = []

setup(
    name=about["__package_name__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=about["__long_descr__"],
    long_description_content_type="text/markdown",
    url=about["__project_url__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=False,
    python_requires=">=3.6",
    install_requires=INSTALL_REQUIRES,
)
