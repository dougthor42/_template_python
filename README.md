# Generic CookieCutter Template for Python

This repo is my generic template for python projects.


## Usage

1.  Clone this repository.
2.  Make a virtual environment.
3.  Install it: `pip install -e .`
    +   If you want to do development: `pip install -e .[dev]`
4.  Run `python create_project.py /path/to/dir`
5.  Answer the questions.


**Note:** The path listed in step for should *not* include the project name.
A new folder will be made for the project, so you'll end up with:

```
/path/to/dir/
  project_name/
    src/
      package_name/
    README.md
    ...
```


## Development Notes

Normally I'd have (a) a package within a `src` dir and (b) a separate top-level
package for tests, but given that this is supposed to just be a script (and
not, for example, something I distribute on pypi or a standalone application),
I've opted to put everything within a `src` dir only.

So all code and tests can be found in `src`. The top-level `create_project.py`
is only to keep the Usage simple (`python create_project.py`).


### Testing

Tests are run with:

```
pytest src/
```

Note: `pyproject.toml` specifies the
[`testpaths`](https://docs.pytest.org/en/latest/reference.html#confval-testpaths)
option which tells pytest to only look for tests in `src/`. Not setting this
option causes pytest to find tests in `{{cookiecutter.project_slug}}/`.
