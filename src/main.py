# -*- coding: utf-8 -*-
"""
"""
import ast
import datetime
import subprocess
from functools import partial
from typing import Tuple

import click
import requests
from cookiecutter.main import cookiecutter

echo = partial(click.secho, fg="yellow", bold=True)


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


def _fix_timestamp(ts: str) -> str:
    """
    Fix the formatting on timestamps to be uniform.

    We know that ``ts`` will only come in two flavors::

       2021-09-05 11:43:40 -0700   # from _get_current_local_commit_info, aware
       2021-07-30T20:57:11Z        # from _get_current_remote_commit_info, naive

    So we unify them into one by parsing both into a datetime object and
    then re-formatting them.
    """
    fmts = ["%Y-%m-%d %H:%M:%S %z", "%Y-%m-%dT%H:%M:%SZ"]
    for fmt in fmts:
        try:
            dt = datetime.datetime.strptime(ts, fmt)
            break
        except ValueError:
            continue
    else:
        raise ValueError(f"`{ts}` does not match any of the accepted datetime formats.")

    # Convert everything to UTC
    if ts.endswith("Z"):
        # Strptime will return a naive datetime object in this case, so we
        # have to force it to be aware with timezone = utc.
        dt = dt.replace(tzinfo=datetime.timezone.utc)

    dt = dt.astimezone(datetime.timezone.utc)

    return dt.isoformat(sep=" ")


def _check_repo() -> None:
    """
    Check what version the user has against remote and warn if an update is
    available.

    This is a fairly simple and naive version check. If the user has local
    commits, then we don't display the the behind/ahead commit count.
    """
    remote_url = "https://api.github.com/repos/dougthor42/_template_python"

    local_hash, local_date = _get_current_local_commit_info()
    remote_hash, remote_date = _get_current_remote_commit_info(remote_url)

    local_date = _fix_timestamp(local_date)
    remote_date = _fix_timestamp(remote_date)

    # Figure out how many commits we are behind.
    remote_msg = f"  Remote: {remote_hash:<10} / {remote_date}"
    try:
        commit_qty = _get_diff_total_commits(remote_url, local_hash, remote_hash)
        commits_ahead = str(commit_qty) + " " + pluralize("commit", commit_qty)

        remote_msg += f" / {commits_ahead} ahead"
    except WebApiError:
        # We can't figure out how many commits we are ahead, likely because
        # the user has local commits that don't exist in the remote.
        pass

    # print the warning
    echo("A new version of this template is available.")
    echo(f"  Local:  {local_hash:<10} / {local_date}")
    echo(remote_msg)
    echo("It's recommended that you abort (CTRL-C) and then run `git pull`.")


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
    _check_repo()

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
