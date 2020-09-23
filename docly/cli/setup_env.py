import os
from pathlib import Path

from docly.ioutils import download_from_url, print_on_console


def inspect_and_download_latest_model(model_root: Path, download_url: str) -> bool:
    model_file = "code2doc_py.mdl"
    if not model_root.exists():
        os.makedirs(str(model_root))
        os.mkdir(str(model_root / "model"))
    if Path(model_root/ "model" / model_file).exists() and Path(model_root/ "model" / model_file).is_file():
        return True
    else:
        print_on_console("There is no model. Downloading", color="red")
        download_from_url(download_url, str(Path(model_root/ "model" / model_file)))
        print("Download finished, processing the files")
        return True
