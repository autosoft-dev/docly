from pathlib import Path
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import time
import sys
import shutil

from pyfiglet import Figlet
import transformers
from halo import Halo

from .args import setup_cmdline_args_for_docly_gen
from .setup_env import inspect_and_download_latest_model, inspect_and_download_latest_tslibs
from docly.config import DoclyConfig
from docly.ioutils import (is_dir,
                           check_out_path,
                           process_file,
                           is_python_file,
                           is_ipynb_notebook,
                           query_yes_no,
                           look_for_update
                           )
from docly.ioutils.console_printer import print_on_console
from docly.ioutils.apply_diff import apply_diff
from docly.ioutils.table_printer import print_results_as_table
from docly.ioutils.convert_ipynb import convert_ipynb_to_python
from docly.logic.logic_main import load_model, predict_docstring

transformers.logger.setLevel(transformers.logging.CRITICAL)

parser = ArgumentParser()
ROOT = (Path.home() / ".docly")
MODEL_DOWNLOAD_ROOT = "https://docly-model.s3.amazonaws.com/pytorch_model.bin"
TSLIBS_DOWNLOAD_ROOT = "https://func2docstr-py.s3.amazonaws.com/"

f = Figlet(font='slant')


def _print_welcome():
    print(f.renderText('Docly'))


# def _predict_docstrings_from_file(f_path: Path, ts_lib_path: str, model: object, tokenizer: object):
#     func_names = []
#     ct = []
#     for code_tokens, raw_code, start_index, function_name in process_file(f_path, ts_lib_path):
#         func_names.append(func_names)
#         ct.append(code_tokens)
#     docstrs = predict_docstring(model, tokenizer, ct)
#     print(docstrs)


def _apply_diff(docstr_loc, no_generate_args_list, ipynb_files):
    print_on_console("Applying diff", color="green")
    apply_diff(docstr_loc, no_generate_args_list, ipynb_files)
    print_on_console("Diff applied. Good bye!", color="green", emoji="thumbsup")


def _remove_converted_python_files(ipynb_files):
    for py_file_loc, _ in ipynb_files.items():
        Path(py_file_loc).unlink()


def _if_jupytext_is_installed():
    try:
        import jupytext
        return True
    except ModuleNotFoundError:
        return False


def _deal_with_result(args, table_rows, docstr_loc, ipynb_files):
    if not args.no_generate_diff and table_rows:
        print_results_as_table(table_rows)
    elif args.no_generate_diff and docstr_loc:
        if args.no_print_report:
            choice = query_yes_no("The diff has been generated, do you want to see the suggestions for missing Docstrings?")
            if choice:
                print_results_as_table(table_rows)
                choice = query_yes_no("Do you want to apply the suggestions?")
            else:
                choice = query_yes_no("Do you want to apply the suggestions?")
        else:
            choice = query_yes_no("Do you want to apply the suggestions?")
        
        if choice:
            _apply_diff(docstr_loc, args.no_generate_args_list, ipynb_files)
        else:
            _remove_converted_python_files(ipynb_files)
            print_on_console("Nothing changed. Good bye!", color="green", emoji="thumbsup")
    else:
        print_on_console("\n\nNothing to be done. Good bye!", color="green", emoji="thumbsup")


@Halo(text='Processing files', spinner='dots')
def _process(args, model, tokenizer, ts_lib_path, config: DoclyConfig):
    """
    Terribly written code. Refactor ASAP
    """
    table_rows = []
    docstr_loc = {}  # Very badly named variable. Need to change
    ipynb_files = {}

    for file in args.files:
        f_path = Path(file)
        if is_dir(file):
            for f in check_out_path(f_path):
                if not is_dir(f) and is_python_file(f):
                    ####
                    # Very bad implementation. Change ASAP
                    ####
                    if not config.is_dir_skipped(str(f).split("/")[:-1]):
                        for code_tokens, params, start_index, function_name, ds in process_file(f, ts_lib_path):
                            if ds == "":
                                docstr = predict_docstring(model, tokenizer, [code_tokens])
                                if docstr_loc.get(str(f)) is None:
                                    docstr_loc[str(f)] = {start_index[0]: 
                                                                (start_index[1], 
                                                                docstr[0], 
                                                                params
                                                                )
                                                         }
                                else:
                                    docstr_loc[str(f)][start_index[0]] = (start_index[1], 
                                                                          docstr[0],
                                                                          params)
                                table_rows.append([f.name, function_name, docstr[0]])
                elif not is_dir(f) and is_ipynb_notebook(f) and args.run_on_notebooks:
                    if not config.is_dir_skipped(str(f).split("/")[:-1]):
                        py_file = convert_ipynb_to_python(f)
                        for code_tokens, params, start_index, function_name, ds in process_file(py_file, ts_lib_path):
                            if ds == "":
                                docstr = predict_docstring(model, tokenizer, [code_tokens])
                                if docstr_loc.get(str(py_file)) is None:
                                        docstr_loc[str(py_file)] = {start_index[0]: 
                                                                        (start_index[1], 
                                                                        docstr[0], 
                                                                        params
                                                                        )
                                                                    }
                                else:
                                    docstr_loc[str(py_file)][start_index[0]] = (start_index[1], 
                                                                                docstr[0],
                                                                                params)
                                table_rows.append([f.name, function_name, docstr[0]])
                                ipynb_files[str(py_file.absolute())] = f
        else:
            if is_python_file(f_path):
                if not config.is_dir_skipped(str(f_path.absolute()).split("/")[:-1]):
                    for code_tokens, params, start_index, function_name, ds in process_file(f_path, ts_lib_path):
                        if ds == "":
                            docstr = predict_docstring(model, tokenizer, [code_tokens])
                            if docstr_loc.get(str(f_path.absolute())) is None:
                                docstr_loc[str(f_path.absolute())] = {start_index[0]: 
                                                                        (start_index[1], 
                                                                        docstr[0],
                                                                        params
                                                                        )
                                                                     }
                            else:
                                docstr_loc[str(f_path.absolute())][start_index[0]] = (start_index[1], 
                                                                                    docstr[0],
                                                                                    params)
                            table_rows.append([f_path.name, function_name, docstr[0]])
            elif is_ipynb_notebook(f_path) and args.run_on_notebooks:
                if not config.is_dir_skipped(str(f_path.absolute()).split("/")[:-1]):
                    py_file = convert_ipynb_to_python(f_path)
                    for code_tokens, params, start_index, function_name, ds in process_file(py_file, ts_lib_path):
                        if ds == "":
                            docstr = predict_docstring(model, tokenizer, [code_tokens])
                            if docstr_loc.get(str(py_file)) is None:
                                    docstr_loc[str(py_file)] = {start_index[0]: 
                                                                    (start_index[1], 
                                                                    docstr[0],
                                                                    params
                                                                    )
                                                                }
                            else:
                                docstr_loc[str(py_file)][start_index[0]] = (start_index[1], 
                                                                            docstr[0],
                                                                            params)
                            table_rows.append([f_path.name, function_name, docstr[0]])
                            ipynb_files[str(py_file.absolute())] = f_path.absolute()
    return table_rows, docstr_loc, ipynb_files



def main():
    if look_for_update():
        print_on_console("There is an update available. Please run `pip install --upgrade docly`", color="green", emoji="rotating_light")
    _print_welcome()
    
    setup_cmdline_args_for_docly_gen(parser)
    args = parser.parse_args()

    if args.run_on_notebooks and not _if_jupytext_is_installed():
        print_on_console("You have mentioned `run_on_notebooks` but the needed dependecy is not present. Please run `pip install 'docly[jupyter]'` for that. This switch will be ignored", color="green")
        args.run_on_notebooks = False
    
    # if args.run_on_notebooks:
    #     print_on_console("You have mentioned the `run_on_notebooks` switch. It is experimental", color="red", emoji="rotating_light")
    #     choice = query_yes_no("Do you want to continue?")
    #     if not choice:
    #         args.run_on_notebooks = False

    config = DoclyConfig(args.config_file)

    try:
        inspect_and_download_latest_model(ROOT, MODEL_DOWNLOAD_ROOT)
    except KeyboardInterrupt:
        print_on_console("You stopped the download. Docly won't work", color="red", emoji="X")
        shutil.rmtree(str(ROOT / "model"))
        sys.exit(1)
    
    try:
        ready, tslib_file = inspect_and_download_latest_tslibs(ROOT, TSLIBS_DOWNLOAD_ROOT)
        if not ready:
            print_on_console("===== OS version not supported =====", color="red", emoji="X")
            return
    except KeyboardInterrupt:
        print_on_console("You stopped the download. Docly won't work", color="red", emoji="X")
        sys.exit(1)

    print_on_console("Loading Engine. Please wait", color="green")
    model, tokenizer = load_model(str(ROOT / "model"/ "pytorch_model.bin"))
    print_on_console("Engine Loaded.", color="green", emoji="heavy_check_mark")
    ts_lib_path = str(ROOT / "tslibs" / tslib_file)
    
    table_rows, docstr_loc, ipynb_files = _process(args, model, tokenizer, ts_lib_path, config)

    _deal_with_result(args, table_rows, docstr_loc, ipynb_files)
