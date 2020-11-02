from pathlib import Path
import logging

from invoke import run


IPYNB_TO_PY_CMD = "jupytext --to py"
PY_TO_IPYNB_CMD = "jupytext --to notebook"


def convert_ipynb_to_python(notebook_path: Path):
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