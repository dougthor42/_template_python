# Generic CookieCutter Template for Python

This repo is my generic template for python projects.


## Usage

1.  Clone this repository.
2.  Make a virtual environment.
3.  Install requirements: `pip install -r requirements.txt`
    +   Note: this installs dev requirements too, but you don't need to worry
        about that.
4.  Run `create_project.py`
5.  Answer the questions.


## Development Notes

Normally I'd have (a) a package within a `src` dir and (b) a separate top-level
package for tests, but given that this is supposed to just be a script (and
not, for example, something I distribute on pypi or a standalone application),
I've opted to put everything within a `src` dir only.

So all code and tests can be found in `src`. The top-level `create_project.py`
is only to keep the Usage simple (`python create_project.py`).
