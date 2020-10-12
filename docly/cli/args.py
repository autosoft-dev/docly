from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
from pathlib import Path


def setup_cmdline_args(parser: ArgumentParser):
    parser.add_argument("--no_generate_diff", action="store_false")
    parser.add_argument("--print_report", action="store_true")
    parser.add_argument("files", type=str, nargs="+",
                         help="List the files/dirs you want to run it on")