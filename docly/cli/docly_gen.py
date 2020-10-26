from pathlib import Path
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import time

from pyfiglet import Figlet
import transformers
from halo import Halo

from .args import setup_cmdline_args_for_docly_gen
from .setup_env import inspect_and_download_latest_model, inspect_and_download_latest_tslibs
from docly.config import DoclyConfig
from docly.ioutils import (print_on_console,
                           is_dir,
                           check_out_path,
                           process_file,
                           is_python_file,
                           query_yes_no,
                           look_for_update
                           )
from docly.ioutils.apply_diff import apply_diff
from docly.ioutils.table_printer import print_results_as_table
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


def _deal_with_result(args, table_rows, docstr_loc):
    if args.print_report:
        print_results_as_table(table_rows)
    if args.no_generate_diff and docstr_loc:
        if not args.print_report:
            choice = query_yes_no("The diff has been generated, do you want to see the suggestions for missing Docstrings?")
            if choice:
                print_results_as_table(table_rows)
                choice = query_yes_no("Do you want to apply the suggestions?")
            else:
                choice = query_yes_no("Do you want to apply the suggestions?")
        else:
            choice = query_yes_no("Do you want to apply the suggestions?")
        
        if choice:
            print_on_console("Applying diff", color="green")
            apply_diff(docstr_loc, args.no_generate_args_list)
            print_on_console("Diff applied. Good bye!", color="green")
        else:
            print_on_console("Nothing changed. Good bye!", color="green")
    else:
        print_on_console("\n\nNothing to be done. Good bye!", color="green")


@Halo(text='Processing files', spinner='dots')
def _process(args, model, tokenizer, ts_lib_path, config: DoclyConfig):
    table_rows = []
    docstr_loc = {}  # Very badly named variable. Need to change

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
                                    docstr_loc[str(f)] = {start_index[0]: (start_index[1], 
                                                                        docstr[0], 
                                                                        params)}
                                else:
                                    docstr_loc[str(f)][start_index[0]] = (start_index[1], 
                                                                        docstr[0],
                                                                        params)
                                table_rows.append([f.name, function_name, docstr[0]])
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
                                                                    params)}
                            else:
                                docstr_loc[str(f_path.absolute())][start_index[0]] = (start_index[1], 
                                                                                    docstr[0],
                                                                                    params)
                            table_rows.append([f_path.name, function_name, docstr[0]])
    return table_rows, docstr_loc



def main():
    if look_for_update():
        print("There is an update available. Please run `pip install --upgrade docly`")
    _print_welcome()
    
    setup_cmdline_args_for_docly_gen(parser)
    args = parser.parse_args()
    config = DoclyConfig(args.config_file)
    
    # print(args.print_report)
    
    inspect_and_download_latest_model(ROOT, MODEL_DOWNLOAD_ROOT)
    ready, tslib_file = inspect_and_download_latest_tslibs(ROOT, TSLIBS_DOWNLOAD_ROOT)
    if not ready:
        print_on_console("===== OS version not supported =====", color="red")
        return

    print_on_console("Loading Engine. Please wait", color="green")
    model, tokenizer = load_model(str(ROOT / "model"/ "pytorch_model.bin"))
    print_on_console("Engine Loaded.", color="green")
    ts_lib_path = str(ROOT / "tslibs" / tslib_file)
    
    table_rows, docstr_loc = _process(args, model, tokenizer, ts_lib_path, config)

    _deal_with_result(args, table_rows, docstr_loc)
