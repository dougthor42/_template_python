# -*- coding: utf-8 -*-
"""
# Reference Project

https://foo.bar

A reference project used for testing my CookieCutter template.
"""
from pathlib import Path

__all__ = [
    "__author__",
    "__author_email__",
    "__maintainer_email__",
    "__maintainer_email__",
    "__license__",
    "__version__",
    "__released__",
    "__created__",
    "__project_name__",
    "__project_url__",
    "__package_name__",
    "__description__",
    "__long_descr__",
]

__author__ = "pytest"
__author_email__ = "pytest@foo.bar"

__maintainer__ = ""
__maintainer_email__ = ""

__license__ = "MIT"
__version__ = "0.0.0"
__released__ = ""
__created__ = "2020-07-10"

__project_name__ = "Reference Project"
__project_url__ = "https://foo.bar"
__package_name__ = "reference_proj"

__description__ = "A reference project used for testing my CookieCutter template."
__long_descr__ = __doc__

# Try to read the README file and use that as our long description.
try:
    base_dir = Path(__file__).parent.parent
    readme = base_dir / "README.md"
    __long_descr__ = readme.read_text()
except Exception:
    pass
