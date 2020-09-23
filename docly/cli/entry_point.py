from pathlib import Path
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from pyfiglet import Figlet

from .args import setup_cmdline_args
from .setup_env import inspect_and_download_latest_model


parser = ArgumentParser()
ROOT = (Path.home() / ".docly")
DOWNLOAD_ROOT = "https://func2docstr-py.s3.amazonaws.com/code2doc_py.mdl"

f = Figlet(font='slant')


def _print_welcome():
    print(f.renderText('Docly'))


def main():
    _print_welcome()
    
    setup_cmdline_args(parser)
    args = parser.parse_args()
    
    inspect_and_download_latest_model(ROOT, DOWNLOAD_ROOT)
