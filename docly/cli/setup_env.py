import os
from pathlib import Path
import platform

from docly.ioutils import download_from_url
from docly.ioutils.console_printer import print_on_console

SUPPORTED_PLATFORMS = ["linux", "darwin"]


def inspect_and_download_latest_model(model_root: Path, download_url: str) -> bool:
    model_file = "pytorch_model.bin"

    if not model_root.exists():
        os.makedirs(str(model_root))
        os.mkdir(str(model_root / "model"))
    elif model_root.exists() and not (model_root / "model").exists():
        os.mkdir(str(model_root / "model"))

    if Path(model_root/ "model" / model_file).exists() and Path(model_root/ "model" / model_file).is_file():
        return True
    
    print_on_console("There is no model. Downloading", color="green")
    download_from_url(download_url, str(Path(model_root/ "model" / model_file)))
    print_on_console("Download complete", color="green", emoji="heavy_check_mark")
    return True


def inspect_and_download_latest_tslibs(tslibs_root: Path, download_url: str) -> bool:
    os_name = platform.system().lower()
    if os_name not in SUPPORTED_PLATFORMS:
        return (False, None)
    
    file_name = "python_ts_darwin64.so" if os_name == "darwin" else "python_ts_nix64.so"
    download_url = f"{download_url}{file_name}"

    if (tslibs_root/ "tslibs" / file_name).exists() and (tslibs_root/ "tslibs" / file_name).is_file():
        return (True, file_name) 

    if not (tslibs_root / "tslibs").exists():
        os.mkdir(str(tslibs_root / "tslibs"))
    
    print_on_console("There is no tree-sitter lib. Downloading", color="green")
    download_from_url(download_url, str(Path(tslibs_root/ "tslibs" / file_name)))
    print_on_console("Download complete", color="green", emoji="heavy_check_mark")
    return (True, file_name)
    