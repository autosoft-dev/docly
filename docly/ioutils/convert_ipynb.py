from pathlib import Path
import shutil
import logging

from invoke import run
from docly.ioutils import CACHE_DIR, cache_exists, make_cache_dir


IPYNB_TO_PY_CMD = "jupytext --set-formats ipynb,py:percent"
PY_TO_IPYNB_CMD = "jupytext --update --to ipynb"


def convert_ipynb_to_python(notebook_path: Path):
    actual_file_path = str(notebook_path.absolute())
    cache_file_name = actual_file_path[1:].replace("/", "#")

    if not cache_exists():
        make_cache_dir()
    
    if (CACHE_DIR / cache_file_name).exists():
        (CACHE_DIR / cache_file_name).unlink()
    
    shutil.copy(actual_file_path, str(CACHE_DIR / cache_file_name))

    result = run(f"{IPYNB_TO_PY_CMD} {str(notebook_path.absolute())}", hide=True, warn=True)
    if not result.ok:
        logging.error("Could not run the conversion command. Maybe use `pip install 'docly[jupyter]'")
        return None
    else:
        return (notebook_path.absolute().parent / (notebook_path.stem + '.py')).absolute()


def convert_python_to_ipynb(python_file_path: Path):
    result = run(f"{PY_TO_IPYNB_CMD} {str(python_file_path.absolute())}", hide=True, warn=True)
    if not result.ok:
        logging.error("Could not run the conversion command. Maybe use `pip install 'docly[jupyter]'")
    else:
        return (python_file_path.absolute().parent / (python_file_path.stem + '.ipynb')).absolute()