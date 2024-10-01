import os
import string
import numpy as np

from console import ERROR_CONSOLE

def clear():
    # credit: https://stackoverflow.com/questions/2084508/clear-the-terminal-in-python
    os.system('cls' if os.name == 'nt' else 'clear')

def get_file(path: str) -> (str | None):
    ret = None
    try:
        with open(path) as f:
            ret = f.read()
    except FileNotFoundError:
        ERROR_CONSOLE.print("Could not find file!")

    return ret

def get_file_bytes(path: str) -> (bytes | None):
    ret = None
    try:
        with open(path, "rb") as f:
            ret = f.read()
    except FileNotFoundError:
        ERROR_CONSOLE.print("Could not find file!")

    return ret

def generate_key() -> bytes:
    secret_key = os.urandom(16)
    return secret_key

def generate_random_variable(length: int) -> str:
    chars = string.ascii_letters
    return "".join(np.random.choice(list(chars), length, True))