# -*- coding: utf-8 -*-
"""
"""
import ast
import datetime

import click
from cookiecutter.main import cookiecutter


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
