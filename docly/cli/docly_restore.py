from pathlib import Path
import os
import shutil

from docly.ioutils.apply_diff import CACHE_DIR
from docly.ioutils import check_out_path, is_dir, is_python_file, print_on_console, query_yes_no


def get_all_files_from_cache():
    return os.listdir(str(CACHE_DIR))


def main():
    all_cached_files = get_all_files_from_cache()
    choice = query_yes_no("It will restore all MODIFIED files to the state of last run of `docly-gen`. Are you sure?")
    if choice:
        print_on_console("Restoring files", color="green")
        try:
            for file in check_out_path(Path().cwd().absolute()):
                if not is_dir(file) and is_python_file(file):
                    full_path = str(Path(file).absolute())
                    comparison_key = full_path[1:].replace("/", "#")
                    if comparison_key in all_cached_files:
                        source_file = str(CACHE_DIR / comparison_key)
                        final_file = str(Path(file).absolute())
                        shutil.move(source_file, final_file)
            print_on_console("Restoring done", color="green")
        except KeyboardInterrupt:
            print_on_console("Restoration not finished", color="red")