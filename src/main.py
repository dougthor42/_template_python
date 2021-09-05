# -*- coding: utf-8 -*-
"""
"""
import ast
import datetime
import subprocess
from typing import Tuple

import click
import requests
from cookiecutter.main import cookiecutter


class WebApiError(Exception):
    pass


def _get_current_local_commit_info() -> Tuple[str, str]:
    """
    Get the current local commit information.

    Returns a two-tuple of (hash, datetime).
    """
    cmd = ["git", "rev-parse", "HEAD"]
    # reminder: catpure_output was added in 3.7   :-(
    proc = subprocess.run(cmd, stdout=subprocess.PIPE)
    commit_hash = proc.stdout.strip().decode("utf-8")

    # From https://stackoverflow.com/a/51403241/1354930
    cmd = ["git", "--no-pager", "log", "-1", "--format='%ai'"]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE)
    commit_date = proc.stdout.strip().decode("utf-8").strip("'")

    return commit_hash, commit_date


def _get_current_remote_commit_info(api_base_url: str) -> Tuple[str, str]:
    """
    Get the current remote repositiory's latest commit information.

    Returns a 2-tuple of (commit_hash, commit_date)..
    """
    # Note: We intentionally do not use `git fetch` because I don't want
    # to make any changes whatsoever to the user's local repo. So instead
    # use the github api.

    resp = requests.get(api_base_url + "/commits/master")
    json = resp.json()

    commit_hash = json["sha"]
    commit_date = json["commit"]["author"]["date"]

    return commit_hash, commit_date


def _get_diff_total_commits(
    api_base_url: str, local_hash: str, remote_hash: str
) -> int:
    compare = f"/compare/{local_hash}...{remote_hash}"

    resp = requests.get(api_base_url + compare)

    if resp.status_code == 404:
        raise WebApiError(
            f"Got 404 for {api_base_url}{compare}. Likely cause"
            f"is that {local_hash} does not exist in the remote (eg: the"
            "user has local commits present)."
        )

    json = resp.json()

    commits_ahead = json["total_commits"]

    return commits_ahead


def pluralize(s: str, n: int) -> str:
    """
    Change ``s`` to plural by simply adding "s".

    A very naive function, but suitable in most cases.
    """
    if abs(n) != 1:
        s += "s"
    return s


def _parse_extra_context(ctx, param, value):
    if value is None:
        return value
    try:
        d = ast.literal_eval(value)
        if isinstance(d, dict):
            return d
        else:
            # Perhaps a stringified-string was passed? Eg:
            # '''"{'author': 'foo'}"'''
            # and so literal_eval just returns the string "{'author': 'foo'}"
            raise Exception
    except Exception:
        raise click.BadParameter("Can't parse value into a dict of literals.")


@click.command()
@click.argument("outdir", type=click.Path(exists=False, file_okay=False))
@click.option(
    "--extra-context",
    default=None,
    help=(
        "A string representation of a python dict of literals used to replace"
        " the default values or prompts for input. Values here are passed"
        " directly to cookiecutter's extra_context arg."
    ),
    callback=_parse_extra_context,
)
def main(outdir, extra_context):
    """
    Create a new project in OUTDIR.

    Note that OUTDIR should *not* contain the project name - CookieCutter
    will create the project directory automatically.
    """
    _default_extra_context = {"create_date": datetime.date.today().isoformat()}
    passed_extra_context = _default_extra_context
    no_input = False

    if extra_context is not None:
        # Note: ordering of the splat matters! We want anyting in the
        # user-provided extra_context to override the default extra context
        # so _default_extra_context must be first.
        passed_extra_context = {**_default_extra_context, **extra_context}
        no_input = True

    cookiecutter(
        template=".",
        extra_context=passed_extra_context,
        output_dir=outdir,
        no_input=no_input,
    )


if __name__ == "__main__":
    main()
