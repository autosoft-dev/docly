import os
from pathlib import Path
import requests
import shutil

from tqdm import tqdm
from clint.textui import puts, colored

from c2nl.parser import parser as py_parser
from c2nl.tokenizers import CodeTokenizer
# from c2nl.objects import Code


def is_dir(file_or_dir_path):
    if isinstance(file_or_dir_path, Path):
        return file_or_dir_path.is_dir()
    elif isinstance(file_or_dir_path, str):
        return Path(file_or_dir_path).is_dir()
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
    tokenizer = CodeTokenizer()
    # code = Code()
    if result:
        for func_name, data in py_parser.get_func_body_and_docstr(parser_obj):
            # print(py_toeknizer.tokenize_code_string(func_body))
            # code.tokens = tokenizer.tokenize(func_body).data
            # code.text = func_body
            (func_body, docstr), start, end = data
            ret_start = (start[0]+1, start[1])
            yield tokenizer.tokenize(func_body).data, func_body, ret_start, func_name
