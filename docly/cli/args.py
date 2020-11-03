from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
from pathlib import Path


def setup_cmdline_args_for_docly_gen(parser: ArgumentParser):
    parser.add_argument("--no_generate_diff", action="store_false", 
                        help="Do not generate the diff. Only prints a report on the console")
    parser.add_argument("--no_generate_args_list", action="store_false",
                        help="Do not generate argument list in the docstring")
    parser.add_argument("--no_print_report", action="store_false",
                        help="Do not prompt to show the report once the diff is generated")
    parser.add_argument("--run_on_notebooks", action="store_true",
                        help="!!EXPERIMENTAL!! If you want docly to run on notebook (.ipynb) files (Requires jupytext and defaults false)")
    #####################
    # Unused at the moment.
    parser.add_argument("--docstring_style", type=str, default="google", 
                        help="What style of docstring you want. Defaults to Google style")
    #####################
    parser.add_argument("--config_file", type=str, default="docly-config.ini",
                        help="Configuration file for docly")
    parser.add_argument("files", type=str, nargs="+",
                         help="List the files/dirs you want to run it on")


def setup_cmdline_args_for_docly_restore(parser: ArgumentParser):
    parser.add_argument("--force", action="store_true", 
                        help="Disables interactive restoring")