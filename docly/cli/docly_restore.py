from argparse import ArgumentParser
from pathlib import Path
import os
import shutil

from .args import setup_cmdline_args_for_docly_restore
from docly.ioutils.apply_diff import CACHE_DIR
from docly.ioutils import check_out_path, is_dir, is_python_file, query_yes_no, is_ipynb_notebook
from docly.ioutils.console_printer import print_on_console

parser = ArgumentParser()


def get_all_files_from_cache():
    return os.listdir(str(CACHE_DIR))


def main():
    setup_cmdline_args_for_docly_restore(parser)
    args = parser.parse_args()
    all_cached_files = get_all_files_from_cache()
    if not args.force:
        choice = query_yes_no("It will restore all MODIFIED files to the state of last run of `docly-gen`. Are you sure?")
    else:
        # Forceful application of restore command
        choice = True
    if choice:
        print_on_console("Restoring files", color="green")
        try:
            for file in check_out_path(Path().cwd().absolute()):
                if not is_dir(file) and (is_python_file(file) or is_ipynb_notebook(file)):
                    full_path = str(Path(file).absolute())
                    comparison_key = full_path[1:].replace("/", "#")
                    if comparison_key in all_cached_files:
                        source_file = str(CACHE_DIR / comparison_key)
                        final_file = str(Path(file).absolute())
                        shutil.move(source_file, final_file)
            print_on_console("Restoring done", color="green", emoji="thumbsup")
        except KeyboardInterrupt:
            print_on_console("Restoration not finished", color="red", emoji="X")