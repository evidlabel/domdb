import argparse
from typing import Optional
from domdb.core.download_verdicts import load_next_batch
from domdb.core.json2bib import main as json2bib_main
from domdb.core.config import load_config


def create_parser() -> argparse.ArgumentParser:
    """Create the main CLI parser with subcommands."""
    config = load_config()
    parser = argparse.ArgumentParser(
        description="domdb: Tools for citing Danish judicial verdicts in LaTeX"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Download verdicts subcommand
    download_parser = subparsers.add_parser(
        "download-verdicts",
        help="Download verdicts from domsdatabasen.dk",
    )
    download_parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default=config["cases_directory"],
        help="Directory to save JSON case files",
    )

    # JSON to BibTeX subcommand
    bib_parser = subparsers.add_parser(
        "json2bib",
        help="Convert JSON case files to BibTeX format",
    )
    bib_parser.add_argument(
        "-n",
        "--number",
        type=int,
        help="Maximum number of verdicts to process",
    )
    bib_parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default=config["cases_directory"],
        help="Directory containing JSON case files",
    )
    bib_parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=config["bib_output"],
        help="Output BibTeX file path",
    )

    return parser


def main(args: Optional[list] = None) -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(args)

    if not args.command:
        parser.print_help()
        exit(1)

    if args.command == "download-verdicts":
        try:
            count = load_next_batch(directory=args.directory)
            print(f"Successfully fetched {count} cases")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            exit(1)
    elif args.command == "json2bib":
        json2bib_main(args)


if __name__ == "__main__":
    main()
