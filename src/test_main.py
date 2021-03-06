# -*- coding: utf-8 -*-
"""
"""
import difflib
import os
from pathlib import Path

from click.testing import CliRunner

from . import DATA_DIR
from . import main


def _all_files_relative(path):
    """
    Return a list of all files in the path, relative to the path.

    To make things a little easier for development, vim swapfiles are ignored.
    """
    files = []
    for root, _, filenames in os.walk(path):
        for name in filenames:
            r = Path(root, name).relative_to(path)
            if r.suffix == ".swp":
                continue
            files.append(r)
    return files


def _assert_dirs_equal(actual, expected):
    """
    Compare two directories, asserting that their contents match exactly.

    The AssertionError that's raised attempts to contain all differences, not
    just the first difference.

    Parameters
    ----------
    actual, expected : :class:`pathlib.Path`
        The directories to compare. Everything is compared to ``expected``.

    Returns
    -------
    None

    Raises
    ------
    AssertionError

    Notes
    -----
    This might also be possible to write using :class:`filecmp.dircmp`.
    However, initial investigation showed that the ``dircmp`` class didn't
    have a suitable high-level API for doing so (recursive checking of the
    ``dircmp.subdirs`` attribute... bleh).

    If future work wants to switch this to ``dircmp``, you'll likely need
    to subclass ``dircmp`` and mokneypatch the ``phase3`` function because
    ``dircmp`` only does shallow comparisons and we are interested in deep
    comparisons. See
    https://stackoverflow.com/q/4187564/1354930 and
    https://stackoverflow.com/a/24860799/1354930
    """
    # Get a list of all the files in each actual and expected directories
    actual_files = _all_files_relative(actual)
    expected_files = _all_files_relative(expected)

    # Asserting that the *sets* are equal tells us about both missing and extra files.
    assert set(actual_files) == set(expected_files)

    # Diff the contents of each file that exists in both. We don't need to
    # act on the intersection of the two sets because the assert will break
    # us out of this function before we zip things.
    diffs = []
    for a, e in zip(actual_files, expected_files):
        # Build the absolute paths
        a_absolute = actual / a
        e_absolute = expected / e

        a_lines = a_absolute.read_text().split("\n")
        e_lines = e_absolute.read_text().split("\n")

        d = difflib.unified_diff(
            a_lines, e_lines, fromfile=str(a_absolute), tofile=str(e_absolute), n=2
        )
        d = list(d)

        # We don't assert here because we want to collect ALL differences
        # before rasing an AssertionError.
        if len(d) != 0:
            # Originally I was adding to a dict with the key being the filename,
            # but the unified diff contains the filename so we can just use a
            # list which results in easier-to-read diffs in pytest.
            diffs.append("\n".join(x.strip() for x in d))

    if len(diffs) != 0:
        # Merge all the diffs into an easy-to-read string.
        # Future me might want to consider defining my own explaination/diff
        # for failed assertions. See
        # https://docs.pytest.org/en/stable/assert.html#defining-your-
        #   own-explanation-for-failed-assertions
        diff_string = "\n\n".join(diffs)
        # This is guarenteed to be false and is only used to (a) ensure the
        # test fails and (b) show the diff.
        assert diff_string == ""


def test_main(tmp_path):
    slug = "reference-proj"
    descr = "A reference project used for testing my CookieCutter template."

    # Until cookiecutter #1433 gets addressed, we need to send in ALL
    # values present in cookiecutter.json to --extra-context and also pass
    # --no-input.
    # https://github.com/cookiecutter/cookiecutter/issues/1433
    # --no-input is automatically added by main.main if --extra-context is
    # given.
    extra_context = {
        "author": "pytest",
        "author_email": "pytest@foo.bar",
        "create_date": "2020-07-10",
        "license": "MIT",
        "package_name": "reference_proj",
        "project_name": "Reference Project",
        "project_short_description": descr,
        "project_slug": slug,
        "project_url": f"https://foo.bar",
    }

    args = [str(tmp_path), "--extra-context", f"""{extra_context}"""]

    runner = CliRunner()
    result = runner.invoke(main.main, args)

    assert result.exit_code == 0

    # Check that all our files match the expected.
    assert (tmp_path / slug).exists()
    _assert_dirs_equal(actual=tmp_path, expected=DATA_DIR)
