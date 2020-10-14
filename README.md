# docly

![Docly - Automatic source code commenting](https://github.com/autosoft-dev/docly/blob/master/logo/docly.png)

[![parser: tree-hugger](https://img.shields.io/badge/parser-tree--hugger-lightgrey)](https://github.com/autosoft-dev/tree-hugger/)

Automatically generate docstrings for your python functions


## Installing

Requires python 3.6+

First install setuptools-rust by 

```
pip install setuptools-rust
```

Then

```
pip install docly
```

## Using

To generate comments - 

```
docly-gen /path/to/file_or_folder_with_python_files
```

It will produce something like this (Shown on a single file but you can run it on a directory full of files also)

```
The diff has been generated, do you want to see the suggestions for missing Docstrings? [Y/n]
Y
+-----------------+------------------------------+---------------------------------------+
| File Name       | Function Name                | Docstring                             |
+-----------------+------------------------------+---------------------------------------+
| simple_funcs.py | add                          | Add two numbers .                     |
| simple_funcs.py | check_if_even                | Checks if number is even .            |
| simple_funcs.py | check_even_numbers_in_a_list | Return list of numbers in base_list . |
| simple_funcs.py | open_file                    | Open a file .                         |
+-----------------+------------------------------+---------------------------------------+
Do you want to apply the suggestions? [Y/n]
Y
Applying diff
Diff applied. Good bye!
```

Instead if you just want the above report and not to apply the chages then do this - 

```
docly-gen --no_generate_diff --print_report /path/to/file_or_folder_with_python_files
```

If you want to revert the changes we applied then use

```
docly-restore
```

This will bring back ALL the files that we had touched to the exact state before we applied the changes
