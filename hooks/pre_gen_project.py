# -*- coding: utf-8 -*-
"""
Various checks that are run before generating the project (but after the
user has entered values).

Creating new checks:

+ All checks MUST be functions that take no arguments.
+ These functions SHOULD be prefixed with "check_" (similar to how all unit
  tests are "test_foo").
+ The functions MUST return either `True` or `False`.
+ The functions MUST start with _print_hook_name()
+ The functions MUST run `print(PASS)` on success and `print(FAIL)` on failure.

Add any new checks to the `checks` list in `main()`.
"""
import inspect
import re
import sys

import colorama
from colorama import Back
from colorama import Fore
from colorama import Style

colorama.init()

PASS = Fore.WHITE + Back.GREEN + "Passed" + Style.RESET_ALL
FAIL = Fore.WHITE + Back.RED + "Failed" + Style.RESET_ALL


def _print_hook_name():
    name = inspect.stack()[1][3]
    print("{:.<50s}".format(name), end="")


def check_project_name():
    _print_hook_name()

    project_name = "{{ cookiecutter.project_name }}"

    if project_name == "":
        print(FAIL)
        print("  Project name cannot be blank.")
        return False
    else:
        print(PASS)
        return True


def check_package_name():
    _print_hook_name()

    name = "{{ cookiecutter.package_name }}"
    pattern = r"^[a-zA-Z][_a-zA-Z0-9]+$"
    if not re.match(pattern, name):
        print(FAIL)
        print(f"  '{name}' is not a valid Python package name.")
        return False
    else:
        print(PASS)
        return True


def main():
    """
    """
    print("Running pre-generate hooks:")
    results = []
    checks = [check_project_name, check_package_name]
    for check in checks:
        result = check()
        results.append(result)

    return all(results)


if __name__ == "__main__":
    okay = main()
    if not okay:
        # exits with status 1 to indicate failure
        sys.exit(1)
