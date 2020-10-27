from rich.table import Table
from rich.console import Console


def print_results_as_table(rows):
    table = Table(title="Functions and Docstrings")

    table.add_column("File Name", justify="left")
    table.add_column("Function Name", justify="left")
    table.add_column("Docstring", justify="left")

    for row in rows:
        table.add_row(*row)
    
    console = Console()
    console.print(table)
