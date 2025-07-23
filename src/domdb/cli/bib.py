from typing import Optional

import rich_click as click

from domdb.core.converters.json2bib.convert import convert_json_to_bib
from domdb.core.exceptions import ConversionError
from domdb.core.config import load_config


@click.command("bib")
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
    "-f",
    "--file",
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
