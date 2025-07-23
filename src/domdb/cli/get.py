import rich_click as click

from domdb.core.download.main import load_next_batch
from domdb.core.exceptions import DownloadError
from domdb.core.config import load_config


@click.command("get")
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
