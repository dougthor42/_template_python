"""
"""
import difflib
import os
import re
from pathlib import Path

import pytest
import requests
from click.testing import CliRunner

from . import DATA_DIR
from . import main


@pytest.fixture
def extra_context():
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
        "project_url": "https://foo.bar",
        "project_host": "GitHub",
        "create_ci_file": "n",
    }

    yield extra_context


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


@pytest.mark.parametrize(
    "str, n, want",
    [
        ("commit", 1, "commit"),
        ("commit", -1, "commit"),
        ("commit", 2, "commits"),
        ("commit", -2, "commits"),
        ("foobar", 0, "foobars"),
    ],
)
def test_pluralize(str, n, want):
    got = main.pluralize(str, n)
    assert got == want


def test_get_current_local_commit_info():
    got = main._get_current_local_commit_info()
    assert isinstance(got, tuple)
    assert len(got) == 2
    hash_regex = r"[0-9a-f]{40}"
    assert re.fullmatch(hash_regex, got[0])


def test_get_current_remote_commit_info(monkeypatch):
    # Set up some mocking first.
    # See https://docs.pytest.org/en/6.2.x/monkeypatch.html
    class MockResponse:
        status_code = 200

        @staticmethod
        def json():
            rv = {
                "sha": "28d8d1b4e5134676ebe94e9c014a497221370e8b",
                "commit": {"author": {"date": "2021-09-05T13:24:37Z"}},
            }
            return rv

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    # Now we can actually test
    got = main._get_current_remote_commit_info("foo")
    assert isinstance(got, tuple)
    assert len(got) == 2
    hash_regex = r"[0-9a-f]{40}"
    assert re.fullmatch(hash_regex, got[0])


# TODO: This test is, well, pointless.
def test_get_diff_total_commits(monkeypatch):
    class MockResponse:
        status_code = 200

        @staticmethod
        def json():
            rv = {"total_commits": 5}
            return rv

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    got = main._get_diff_total_commits("foo", "111", "222")
    assert got == 5


def test_get_diff_total_commits_raises(monkeypatch):
    class MockResponse:
        status_code = 404

        @staticmethod
        def json():
            rv = {"total_commits": 5}
            return rv

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    with pytest.raises(main.WebApiError):
        main._get_diff_total_commits("foo", "111", "222")


@pytest.mark.parametrize(
    "ts, want",
    [
        ("2021-09-05 11:43:40 -0700", "2021-09-05 18:43:40+00:00"),
        ("2021-07-30T20:57:11Z", "2021-07-30 20:57:11+00:00"),
    ],
)
def test_fix_timestamp(ts, want):
    got = main._fix_timestamp(ts)
    assert got == want


@pytest.mark.parametrize(
    "ts",
    [
        "2021-09-05T11:43:40+0900",  # has "T", no space before offset
        "2021-09-05T11:43:21 -0400",  # has "T"
        "1999-01-03 20:43:19",  # no offset
        "1999-01-03",
        "2021-03-06 12:34:12+0400",  # no space before offset
    ],
)
def test_fix_timestamp_raises(ts):
    with pytest.raises(ValueError):
        main._fix_timestamp(ts)


def test_main(tmp_path, extra_context):
    proj_path = tmp_path / extra_context["project_slug"]

    args = [
        "--no-version-check",
        str(tmp_path),
        "--extra-context",
        f"""{extra_context}""",
    ]

    runner = CliRunner()
    result = runner.invoke(main.main, args)

    assert result.exit_code == 0

    # Check that all our files match the expected.
    assert proj_path.exists()
    _assert_dirs_equal(actual=tmp_path, expected=DATA_DIR)


# Really this is testing the same stuff as `test_main`, but oh well.
def test_main_no_ci(tmp_path, extra_context):
    proj_path = tmp_path / extra_context["project_slug"]

    extra_context["create_ci_file"] = "n"

    args = [
        "--no-version-check",
        str(tmp_path),
        "--extra-context",
        f"""{extra_context}""",
    ]

    runner = CliRunner()
    result = runner.invoke(main.main, args)

    assert result.exit_code == 0

    # No CI files should exist
    for fp in (".github", ".gitlab-ci.yml"):
        ci_file = proj_path / fp
        assert not ci_file.exists()


def test_main_github_ci(tmp_path, extra_context):
    proj_path = tmp_path / extra_context["project_slug"]

    extra_context["project_host"] = "GitHub"
    extra_context["create_ci_file"] = "y"

    args = [
        "--no-version-check",
        str(tmp_path),
        "--extra-context",
        f"""{extra_context}""",
    ]

    runner = CliRunner()
    result = runner.invoke(main.main, args)

    assert result.exit_code == 0

    # The .github directory should exist
    fp = proj_path / ".github"
    assert fp.exists()
    assert fp.is_dir()

    # And all other CI files should not.
    assert not (proj_path / ".gitlab_ci.yml").exists()


# Yeah, this looks eerily similar to test_main_github_ci, but the difference
# between github (directory) and gitlab (file), and the fact that we need to
# assert the **other** doesn't exist, makes combining these two tests into
# a single parametrized one a bit annoying.
def test_main_gitlab_ci(tmp_path, extra_context):
    proj_path = tmp_path / extra_context["project_slug"]

    extra_context["project_host"] = "GitLab"
    extra_context["create_ci_file"] = "y"

    args = [
        "--no-version-check",
        str(tmp_path),
        "--extra-context",
        f"""{extra_context}""",
    ]

    runner = CliRunner()
    result = runner.invoke(main.main, args)

    assert result.exit_code == 0

    # The .gitlab-ci.yml file should exist
    fp = proj_path / ".gitlab-ci.yml"
    assert fp.exists()
    assert fp.is_file()

    # And all other CI files should not.
    assert not (proj_path / ".github").exists()


def test_main_has_cli(tmp_path, extra_context):
    proj_path = tmp_path / extra_context["project_slug"]

    extra_context["has_cli"] = "y"

    args = [
        "--no-version-check",
        str(tmp_path),
        "--extra-context",
        f"""{extra_context}""",
    ]

    runner = CliRunner()
    result = runner.invoke(main.main, args)

    assert result.exit_code == 0

    # pyproject.toml should define an entry point that ends in ".cli:main"
    assert ".cli:main" in open(proj_path / "pyproject.toml", "r").read()

    # The "srs/<package_name>/cli.py" file should exist
    fp = proj_path / "src" / extra_context["package_name"] / "cli.py"
    assert fp.exists()
    assert fp.is_file()
