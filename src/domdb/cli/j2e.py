from typing import Optional

import rich_click as click

from domdb.core.converters.json2evid import convert_json_to_evid
from domdb.core.exceptions import EvidConversionError
from domdb.core.config import load_config


@click.command("j2e")
@click.option(
    "-n",
    "--number",
    type=int,
    default=None,
    help="Maximum number of cases to process",
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
    default="evid",
    help="Output directory for EVID structure",
)
def j2e_command(
    number: Optional[int], directory: str, output: str
):  # Renamed parameter to output for clarity
    """Convert JSON case files to EVID directory structure."""
    try:
        count = convert_json_to_evid(directory, output, number)
        click.echo(f"Converted {count} cases to EVID in {output}")
    except EvidConversionError as e:
        raise click.ClickException(str(e))
