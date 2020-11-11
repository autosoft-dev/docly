import os
from pathlib import Path
import requests
import shutil
import sys
from distutils.version import LooseVersion
import time

from tqdm import tqdm

from docly.parser import parser as py_parser
from docly.tokenizers import tokenize_code_string
from docly import __version__

# from c2nl.objects import Code
UPDATE_CHECK_URL = "http://3.80.2.138:8584/vercheck/check-version/"
# UPDATE_CHECK_URL = "http://127.0.0.1:5000/vercheck/check-version/"

interaction_cache = lambda : Path(Path.home() / ".docly" / "interaction_cache")

CACHE_DIR = (Path().home() / ".docly" / "file_cache")

cache_exists = lambda : CACHE_DIR.exists()
make_cache_dir = lambda : os.mkdir(str(CACHE_DIR))


def _compare_installed_version_with_latest(v1, v2):
    try:
        current_version = LooseVersion(v1)
        latest_version = LooseVersion(v2)
        assert current_version == latest_version
        return True
    except AssertionError:
        return False


def look_for_update():
    with requests.sessions.Session() as s:
        try:
            r = s.get(UPDATE_CHECK_URL, timeout=2)
            r.raise_for_status()
            if not _compare_installed_version_with_latest(__version__, r.text):
                i_c = interaction_cache()
                return True
            return False
        except Exception:
            i_c = interaction_cache()
            if not i_c.exists():
                os.mkdir(i_c)
            if not (i_c / "icache.txt").exists():
                with open((i_c / "icache.txt"), "w") as f:
                    f.write(str(int(time.time())) + "\n")
            else:
                with open((i_c / "icache.txt"), "a") as f:
                    f.write(str(int(time.time())) + "\n")
            return False


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


def is_ipynb_notebook(file_path):
    if isinstance(file_path, Path):
        return file_path.suffix == ".ipynb"
    elif isinstance(file_path, str):
        return Path(file_path).suffix == ".ipynb"
    else:
        return False


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
    func_and_params = parser_obj.get_all_function_names_with_params()
    if result:
        for func_name, data in py_parser.get_func_body_and_docstr(parser_obj):
            # print(py_toeknizer.tokenize_code_string(func_body))
            # code.tokens = tokenizer.tokenize(func_body).data
            # code.text = func_body
            (func_body, docstr), start, end = data
            ret_start = (start[0]+1, start[1])
            params = func_and_params[func_name]
        
            yield tokenize_code_string(func_body), params, ret_start, func_name, docstr.strip()


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