import sys
from typing import Optional
import rich_click as click
from domdb.core.download_verdicts import load_next_batch, DownloadError
from domdb.core.json2bib import convert_json_to_bib, ConversionError
from domdb.core.config import load_config


@click.group(
    chain=True,
    invoke_without_command=True,
    help="Tools for citing Danish judicial verdicts in LaTeX.",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.pass_context
def cli(ctx):
    """Tools for citing Danish judicial verdicts in LaTeX."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        sys.exit(1)


@cli.command("get")
@click.option(
    "-d",
    "--directory",
    default=lambda: load_config()["cases_directory"],
    help="Directory to save JSON case files",
)
def get_command(directory: str):
    """Download verdicts from domsdatabasen.dk."""
    try:
        count = load_next_batch(directory)
        click.echo(f"Successfully fetched {count} cases")
    except DownloadError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {str(e)}")


@cli.command("bib")
@click.option(
    "-n",
    "--number",
    type=int,
    default=None,
    help="Maximum number of verdicts to process",
)
@click.option(
    "-d",
    "--directory",
    default=lambda: load_config()["cases_directory"],
    help="Directory containing JSON case files",
)
@click.option(
    "-o",
    "--output",
    default=lambda: load_config()["bib_output"],
    help="Output BibTeX file path",
)
def bib_command(number: Optional[int], directory: str, output: str):
    """Convert JSON case files to BibTeX format."""
    try:
        count = convert_json_to_bib(directory, output, number)
        click.echo(f"Converted {count} unique cases to {output}")
    except ConversionError as e:
        raise click.ClickException(str(e))


def main():
    cli()


if __name__ == "__main__":
    main()
