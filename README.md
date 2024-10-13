# DD2391-Project

# Ransomware "Bad Day"

## Overview

"Bad Day" is a proof-of-concept ransomware that encrypts files on a system using AES encryption. The AES key is then encrypted with an RSA public key and sent to a remote server (who owns the private key). The user is prompted to pay a ransom to retrieve the decryption key.

This program is a student project and for educational purposes only. 

## Features

- **File Encryption:** Uses AES in CTR mode.
- **File Decryption:** Unlocks files if the correct key is provided.
- **Ransom UI:** A Tkinter window demands a ransom payment for decryption.
- **Targeted File Types:** The program targets known "productivity file formats" such as `.docx`, `.pdf`, but also video and image files like example `.jpg`, and `.mp4`.
- **Public Key Encryption:** AES keys are sent encrypted using a RSA public key to a remote server for storage.
- **Anti-virus protection:** A mixture or payload encryption, string encryption, random file sizes and compilation is used to prevent anti-virus detection.

## How The Ransomware Works

### Encryption:
1. The program searches for files of supported types.
2. Files are encrypted with AES.
3. The AES key is encrypted with RSA and sent to the server.
4. AES key is removed from memory.

### Decryption:
1. The user provides a decryption key.
2. Files are decrypted if the correct key is entered.

## Usage

### Pre-requisites:
- Python 3.x
- Libraries: `pycryptodome`, `tkinter`, `requests`


# Ransomware C2 Server

## Overview

The C2 server handles key generation and distribution for the ransomware. It provides the RSA public key to the client and stores the AES key decrypted by the client.

## Features

- **RSA Key Management:** Generates/stores a 2048-bit RSA key pair.
- **Public Key Endpoint:** Provides the RSA public key.
- **AES Key Storage:** Stores encrypted AES keys from the client.

## Endpoints

1. `/key` (GET): Returns the RSA public key.
2. `/bad_day_key` (POST): Stores the AES key encrypted by the client.
3. `/docs` (GET): Returns API documentation.

## Usage

### Pre-requisites:
- Python 3.x
- Libraries: `pycryptodome`, `fastapi`, `uvicorn`, `pydantic`


### Running:

```bash
fastapi run c2serv.py
```


# Payload Encryptor

## Overview

The `encrypt_payload.py` script encrypts Python payloads using AES in CBC mode. It provides extra features such as compilation, string encryption and randomized file size.

## Features

- **AES Encryption (CBC Mode):** Encrypts payloads securely.
- **Random Variables:** Uses random variable names to obfuscate decryption program.
- **Executable Compilation:** Optionally compiles the payload into an executable.
- **String encryption:** Encrypts all source code strings using AES in ECB mode.
- **Randomized file size:** Appends a random string variable of random length between 5e4 and 1e7.

## Usage

### Pre-requisites:
- Python 3.x
- Libraries: `typer`, `numpy`, `pycryptodome`, `nuitka`

### Commands:

To encrypt payload
```bash
python encrypt_payload.py <payload_path> <save_path>
```

To compile:

```bash
python encrypt_payload.py <payload_path> <save_path> --compile
```

To encrypt strings:

```bash
python encrypt_payload.py <payload_path> <save_path> --encrypt-strings
```

To randomize file size:

```bash
python encrypt_payload.py <payload_path> <save_path> --random-size
```

Help page:

```bash
python encrypt_payload.py --help
```


## Legal Disclaimer

Legal Disclaimer
This software is intended for educational and research purposes only. The developers do not support or condone the use of ransomware or any malicious software in real-world environments. Unauthorized use of this code is illegal and may result in criminal prosecution, fines, or imprisonment.

The authors are not responsible for any misuse or damage caused by this software. Always comply with relevant laws and seek permission before testing or using this code.
