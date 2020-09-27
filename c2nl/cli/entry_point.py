from pathlib import Path
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from pyfiglet import Figlet

from .args import setup_cmdline_args
from .setup_env import inspect_and_download_latest_model, inspect_and_download_latest_tslibs
from c2nl.ioutils import print_on_console, is_dir, check_out_path, process_file, is_python_file
from c2nl.ioutils.table_printer import print_results_as_table
from c2nl.logic import load_model, predict_docstring


parser = ArgumentParser()
ROOT = (Path.home() / ".docly")
MODEL_DOWNLOAD_ROOT = "https://func2docstr-py.s3.amazonaws.com/code2doc_py.mdl"
TSLIBS_DOWNLOAD_ROOT = "https://func2docstr-py.s3.amazonaws.com/"

f = Figlet(font='slant')


def _print_welcome():
    print(f.renderText('Docly'))


def main():
    _print_welcome()
    
    setup_cmdline_args(parser)
    args = parser.parse_args()
    
    inspect_and_download_latest_model(ROOT, MODEL_DOWNLOAD_ROOT)
    ready, tslib_file = inspect_and_download_latest_tslibs(ROOT, TSLIBS_DOWNLOAD_ROOT)
    if not ready:
        print_on_console("===== OS version not supported =====", color="red")
        return

    print_on_console("Loading Engine. Please wait", color="green")
    model = load_model(str(ROOT / "model"/ "code2doc_py.mdl"))
    print_on_console("Engine Loaded. Processing files", color="green")
    ts_lib_path = str(ROOT / "tslibs" / tslib_file)
    table_rows = []
    for file in args.files:
        f_path = Path(file)
        if is_dir(file):
            for f in check_out_path(f_path):
                if not is_dir(f) and is_python_file(f):
                    for code_tokens, raw_code, start_index, function_name in process_file(f, ts_lib_path):
                        docstr, score = predict_docstring(model, code_tokens, raw_code)
                        table_rows.append([f.name, function_name, docstr, round((-1) * score, 2)])
        else:
            if is_python_file(f_path):
                for code_tokens, raw_code, start_index, function_name in process_file(f_path, ts_lib_path):
                    docstr, score = predict_docstring(model, code_tokens, raw_code)
                    table_rows.append([f_path.name, function_name, docstr,  round((-1) * score, 2)])
    print_results_as_table(table_rows)
