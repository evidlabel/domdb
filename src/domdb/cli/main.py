from treeparse import cli, command, group, option
from treeparse.utils.color_config import color_theme

from .download import download
from .bib import bib
from .hay import hay
from .md import md
from .j2e import j2e
from .query import query_count, query_index, query_list

app = cli(
    name="domdb",
    help="Tools for citing Danish judicial verdicts using BibTeX.",
    show_defaults=True,
    theme=color_theme.GITHUB,
    context_settings={"help_option_names": ["-h", "--help"]},
    options=[
        option(
            flags=["-d", "--directory"],
            help="Directory to save JSON case files",
            arg_type=str,
            default="~/domdatabasen/cases",
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

hay_cmd = command(
    name="hay",
    help="Convert JSON case files to Hayagriva YAML format (for Typst).",
    callback=hay,
    options=[
        option(
            flags=["-n", "--number"],
            help="Maximum number of verdicts to process",
            arg_type=int,
            default=-1,
        ),
        option(
            flags=["-o", "--output"],
            help="Output Hayagriva YAML file path",
            arg_type=str,
            default="resources/cases.yml",
        ),
    ],
)
output_cmd.commands.append(hay_cmd)

md_cmd = command(
    name="md",
    help="Convert JSON case files to Markdown format.",
    callback=md,
    options=[
        option(
            flags=["-n", "--number"],
            help="Maximum number of verdicts to process",
            arg_type=int,
            default=-1,
        ),
        option(
            flags=["-o", "--output"],
            help="Output Markdown file path",
            arg_type=str,
            default="resources/cases.md",
        ),
        option(
            flags=["-s", "--split-by-year"],
            help="Split output by year into separate files",
            arg_type=bool,
            default=False,
        ),
        option(
            flags=["-k", "--keyword"],
            dest="keywords",
            help="Filter cases containing ALL given keywords, e.g. -k word1 word2 (case insensitive)",
            arg_type=str,
            nargs="+",
            default=[],
        ),
        option(
            flags=["-f", "--full-text"],
            help="Also search the full verdict body text (HTML/PDF), not just metadata",
            flag=True,
            default=False,
        ),
    ],
)
output_cmd.commands.append(md_cmd)

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

_query_options = [
    option(
        flags=["-k", "--keyword"],
        dest="keywords",
        help="Require ALL keywords (case insensitive); searches metadata, or body with --full-text",
        arg_type=str,
        nargs="+",
        default=[],
        inherit=True,
    ),
    option(
        flags=["-p", "--paragraph"],
        help='Legal paragraph reference, e.g. "straffeloven § 237" or "§ 117 stk. 1"',
        arg_type=str,
        default=None,
        inherit=True,
    ),
    option(
        flags=["--from"],
        dest="from_date",
        help="Verdict date on or after (YYYY-MM-DD)",
        arg_type=str,
        default=None,
        inherit=True,
    ),
    option(
        flags=["--to"],
        dest="to_date",
        help="Verdict date on or before (YYYY-MM-DD)",
        arg_type=str,
        default=None,
        inherit=True,
    ),
    option(
        flags=["-f", "--full-text"],
        help="Also search verdict body text for keywords (paragraph search always includes body)",
        flag=True,
        default=False,
        inherit=True,
    ),
    option(
        flags=["--court"],
        help="Filter by court name (substring match on court/author)",
        arg_type=str,
        default=None,
        inherit=True,
    ),
    option(
        flags=["--subject"],
        help="Filter by case subject (substring match)",
        arg_type=str,
        default=None,
        inherit=True,
    ),
]

query_cmd = group(
    name="query",
    help="Search cached verdicts for legal research.",
)

query_index_cmd = command(
    name="index",
    help="Build metadata index for fast queries (run after downloading new cases).",
    callback=query_index,
    options=_query_options,
)
query_cmd.commands.append(query_index_cmd)

query_count_cmd = command(
    name="count",
    help="Count verdicts matching the query.",
    callback=query_count,
    options=_query_options,
)
query_cmd.commands.append(query_count_cmd)

query_list_cmd = command(
    name="list",
    help="List verdicts matching the query.",
    callback=query_list,
    options=_query_options
    + [
        option(
            flags=["-n", "--number"],
            help="Maximum number of results to list (-1 for all)",
            arg_type=int,
            default=50,
        ),
        option(
            flags=["--format"],
            help="Output format: table or json",
            arg_type=str,
            choices=["table", "json"],
            default="table",
        ),
    ],
)
query_cmd.commands.append(query_list_cmd)

app.subgroups.append(query_cmd)


def main():
    app.run()


if __name__ == "__main__":
    main()
