from prettytable import PrettyTable


def print_results_as_table(rows):
    table = PrettyTable()
    table.field_names = ["File Name", "Function Name", "Docstring"]
    table.align["File Name"] = "l"
    table.align["Function Name"] = "l"
    table.align["Docstring"] = "l"
    for row in rows:
        table.add_row(row)
    
    print(table)
