from pathlib import Path

from tree_hugger.core import PythonParser


def set_up_parser():
    return 


def parse(file_path: str, tslib_path):
    python_parser = PythonParser(library_loc=tslib_path)
    return python_parser.parse_file(file_path), python_parser


def get_func_body_and_docstr(python_parser: PythonParser):
    res = python_parser.get_all_function_bodies(strip_docstr=True, get_index=True)
    for key, value in res.items():
        yield key, value