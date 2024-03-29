"""
Various checks that are run after generating the project.
"""
import inspect
import shutil
import sys
from pathlib import Path

import colorama
from colorama import Back
from colorama import Fore
from colorama import Style

# This is code duplication from pre_gen_project.py. Sadly there's no way
# (that I'm aware of) to make the hooks into a package so that we can use
# a shared module. Adding hooks/__init__.py doesn't work :-(

colorama.init()

PASS = Fore.WHITE + Back.GREEN + "Passed" + Style.RESET_ALL
FAIL = Fore.WHITE + Back.RED + "Failed" + Style.RESET_ALL


def _print_hook_name():
    name = inspect.stack()[1][3]
    print("{:.<50s}".format(name), end="")


# End duplication


PROJECT_DIR = Path.cwd()

CI_FILES = {"GitHub": ".github", "GitLab": ".gitlab-ci.yml"}


def remove_file_or_dir(filepath: str):
    path = PROJECT_DIR / filepath

    if path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(PROJECT_DIR / filepath)
    else:
        raise ValueError(f"The path `{path}` is not a file nor a directory. HOW??")


def remove_cli_file():
    _print_hook_name()

    fp = "src/{{ cookiecutter.package_name }}/cli.py"

    if "{{ cookiecutter.has_cli }}" == "n":
        remove_file_or_dir(fp)
    print("Done")


def remove_ci_files():
    _print_hook_name()

    host = "{{ cookiecutter.project_host }}"

    # User does not want any CI files. Remove them all.
    if "{{ cookiecutter.create_ci_file }}" == "n":
        for file_or_dir in CI_FILES.values():
            remove_file_or_dir(file_or_dir)
        print("Done")
        return

    # User wants a CI file.
    # Create a copy of CI_FILES in case we need it later.
    remove_items = dict(CI_FILES)

    # Delete the item that we want to keep from the dict so that we don't
    # end up removing the file.
    del remove_items[host]

    # Remove all the ones we're **not** using.
    for file_or_dir in remove_items.values():
        remove_file_or_dir(file_or_dir)
    print("Done")


def rename_pyproject_template():
    _print_hook_name()

    # Rename the pyproject.toml.j2 file to just .toml
    # We needed to add the .j2 extension so that `black` would not try to read
    # it as a config file during pre-commit (it fails to parse because of the
    # jinja2 templating code).
    pyproject_file = PROJECT_DIR / "pyproject.toml.j2"
    pyproject_file.rename(PROJECT_DIR / "pyproject.toml")
    print("Done")


def main():
    print("Running post-generate hooks:")
    results = []
    actions = [remove_ci_files, remove_cli_file, rename_pyproject_template]
    for action in actions:
        result = action()
        results.append(result)

    return True


if __name__ == "__main__":
    okay = main()
    if not okay:
        # exits with status 1 to indicate failure
        sys.exit(1)
