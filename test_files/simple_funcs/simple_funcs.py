import os

a_string = """

This is a multi line string

"""

VAR = 50  # A Variable

#####################

#### COMMENT #######

####################

def add(a, b):
    return a * b


def check_even_numbers_in_a_list (base_list):
    return [a for a in base_list if a % 2 == 0]


def open_file(file_path):
    return open(file_path, "r")


def add_tensors (t, t1):
    return t + t1