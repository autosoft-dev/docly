from pathlib import Path

from docly.ioutils.console_printer import print_on_console


def main():
    print_on_console("Cleaning old model", color="green")
    if Path((Path.home() / ".docly" / "model" / "pytorch_model.bin")).exists():
        Path((Path.home() / ".docly" / "model" / "pytorch_model.bin")).unlink()
    print_on_console("Cleaning done", color="green", emoji="heavy_check_mark")
