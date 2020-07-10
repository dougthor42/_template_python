# -*- coding: utf-8 -*-
"""
"""
import datetime

import click
from cookiecutter.main import cookiecutter


@click.command()
@click.argument("outdir", type=click.Path(exists=False, file_okay=False))
def main(outdir):
    """
    Create a new project in OUTDIR.

    Note that OUTDIR should *not* contain the project name - CookieCutter
    will create the project directory automatically.
    """

    cookiecutter(
        template=".",
        extra_context={"create_date": datetime.date.today().isoformat()},
        output_dir=outdir,
    )


if __name__ == "__main__":
    main()
