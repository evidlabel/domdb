import os

from treeparse import cli, command, group, option

from .download import download
from .bib import bib
from .j2e import j2e

app = cli(
    name="domdb",
    help="Tools for citing Danish judicial verdicts using BibTeX.",
    show_defaults=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    options=[
        option(
            flags=["-d", "--directory"],
            help="Directory to save JSON case files",
            arg_type=str,
            default=os.path.expanduser("~/domdatabasen/cases"),
        ),
    ],
)

download_cmd = command(
    name="download",
    help="Download verdicts from domsdatabasen.dk.",
    callback=download,
)
app.commands.append(download_cmd)

output_cmd = group(
    name="output",
    help="Commands for outputting data.",
)

bib_cmd = command(
    name="bib",
    help="Convert JSON case files to BibTeX format.",
    callback=bib,
    options=[
        option(
            flags=["-n", "--number"],
            help="Maximum number of verdicts to process",
            arg_type=int,
            default=-1,
        ),
        option(
            flags=["-o", "--output"],
            help="Output BibTeX file path",
            arg_type=str,
            default="resources/cases.bib",
        ),
    ],
)
output_cmd.commands.append(bib_cmd)

j2e_cmd = command(
    name="j2e",
    help="Convert JSON case files to EVID directory structure.",
    callback=j2e,
    options=[
        option(
            flags=["-n", "--number"],
            help="Maximum number of cases to process",
            arg_type=int,
            default=-1,
        ),
        option(
            flags=["-o", "--output"],
            help="Output directory for EVID structure",
            arg_type=str,
            default="evid",
        ),
    ],
)
output_cmd.commands.append(j2e_cmd)

app.subgroups.append(output_cmd)


def main():
    app.run()


if __name__ == "__main__":
    main()
