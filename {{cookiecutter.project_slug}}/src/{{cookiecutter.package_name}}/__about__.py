# -*- coding: utf-8 -*-
"""
# {{cookiecutter.project_name}}

{{cookiecutter.project_url}}

{{cookiecutter.project_short_description}}
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

__author__ = "{{cookiecutter.author}}"
__author_email__ = "{{cookiecutter.author_email}}"

__maintainer__ = ""
__maintainer_email__ = ""

__license__ = "{{cookiecutter.license}}"
__version__ = "0.0.0"
__released__ = ""
__created__ = "{{cookiecutter.create_date}}"

__project_name__ = "{{cookiecutter.project_name}}"
__project_url__ = "{{cookiecutter.project_url}}"
__package_name__ = "{{cookiecutter.package_name}}"

__description__ = "{{cookiecutter.project_short_description}}"
__long_descr__ = __doc__

# Try to read the README file and use that as our long description.
try:
    base_dir = Path(__file__).parent.parent
    readme = base_dir / "README.md"
    __long_descr__ = readme.read_text()
except Exception:
    pass
