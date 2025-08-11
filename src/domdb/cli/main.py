import sys

import rich_click as click

from .get import get_command
from .bib import bib_command
from .j2e import j2e_command


@click.group(
    chain=True,
    invoke_without_command=True,
    help="Tools for citing Danish judicial verdicts using BibTeX.",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.pass_context
def cli(ctx):
    """Tools for citing Danish judicial verdicts using BibTeX."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        sys.exit(1)


cli.add_command(get_command)
cli.add_command(bib_command)
cli.add_command(j2e_command)


def main():
    cli()


if __name__ == "__main__":
    main()
