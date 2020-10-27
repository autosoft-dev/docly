from rich import print as rprint


def print_on_console(text, color="green", emoji=None):
    if not emoji:
        rprint(f"[{color}]{text}[/{color}]")
    else:
        rprint(f"[{color}]{text}[/{color}]", f":{emoji}:")