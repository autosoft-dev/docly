import os
from pathlib import Path
import requests
import shutil
import sys

from tqdm import tqdm
from clint.textui import puts, colored

from docly.parser import parser as py_parser
from docly.tokenizers import tokenize_code_string

# from c2nl.objects import Code


def is_dir(base_path):
    if isinstance(base_path, Path):
        return base_path.is_dir()
    elif isinstance(base_path, str):
        return Path(base_path).is_dir()
    else:
        return False


def is_python_file(file_path):
    if isinstance(file_path, Path):
        return file_path.suffix == ".py"
    elif isinstance(file_path, str):
        return Path(file_path).suffix == ".py"
    else:
        return False


def print_on_console(text, color="blue"):
    if color == "blue":
        puts(colored.blue(text))
    elif color == "red":
        puts(colored.red(text))
    elif color == "green":
        puts(colored.green(text))
    else:
        puts(text)


def download_from_url(url, dst):
    """
    @param: url to download file
    @param: dst place to put the file
    """
    file_size = int(requests.head(url).headers["Content-Length"])
    if os.path.exists(dst):
        first_byte = os.path.getsize(dst)
    else:
        first_byte = 0
    if first_byte >= file_size:
        return file_size
    header = {"Range": "bytes=%s-%s" % (first_byte, file_size)}
    pbar = tqdm(
        total=file_size, initial=first_byte,
        unit='B', unit_scale=True, desc=dst.split('/')[-1])
    req = requests.get(url, headers=header, stream=True)
    with(open(dst, 'ab')) as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                pbar.update(1024)
    pbar.close()
    return file_size


def check_out_path(target_path: Path):
    """"
    This function recursively yields all contents of a pathlib.Path object
    """
    yield target_path
    for file in target_path.iterdir():
        if file.is_dir():
            yield from check_out_path(file)
        else:
            yield file.absolute()
    

def process_file(file_path: Path, ts_lib_path: str):
    result, parser_obj = py_parser.parse(file_path, ts_lib_path)
    if result:
        for func_name, data in py_parser.get_func_body_and_docstr(parser_obj):
            # print(py_toeknizer.tokenize_code_string(func_body))
            # code.tokens = tokenizer.tokenize(func_body).data
            # code.text = func_body
            (func_body, docstr), start, end = data
            ret_start = (start[0]+1, start[1])
        
            yield tokenize_code_string(func_body), func_body, ret_start, func_name, docstr.strip()


def query_yes_no(question, default="yes"):
    """Ask a yes/no question and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes", "no", or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '{}}'".format(default))

    while True:
        print(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")