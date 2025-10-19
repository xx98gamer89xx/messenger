import nacl.utils
import requests
import time
import pickle
from flask import Flask, request, jsonify
from nacl.public import PrivateKey, PublicKey, Box
from pathlib import Path
external_public_key = 0
identifier = 0
server_url = "http://127.0.0.1:5000/send_message"
private_key_file = Path("private_key")
public_key_file = Path("public_key")
def gen_keys():
    global private_key
    global public_key
    private_key = PrivateKey.generate()
    public_key = private_key.public_key
    with open("private_key", "wb") as f:
        f.write(private_key.encode())
    with open("public_key", "wb") as f:
        f.write(public_key.encode())
    give_information()
def gen_id():
    global identifier
    identifier = input("No tienes nombre, ponlo: ")
    with open("identifier", "w") as f:
        f.write(identifier)


def give_information():
    global public_key_file
    with open(public_key_file, "rb") as f:
        binary_public_key = f.read()
        hex_public_key = binary_public_key.hex()
        print(hex_public_key)

def add_contact():
    global contacts
    try:
        with open("contacts.pkl", "rb") as f:
            contacts = pickle.load(f)
    except:
        contacts = {}
    identifier = input("Identificador del contacto: ")
    hex_public_key = input("Hexadecimal del contacto: ")
    public_key = bytes.fromhex(hex_public_key)
    contacts[identifier] = public_key
    with open("contacts.pkl", "wb") as f:
        pickle.dump(contacts, f)



def send_message():
    global receiver
    global encrypted_message
    global identifier
    data = {"to": receiver, "message": encrypted_message.hex(), "from": identifier}
    response = requests.post(server_url, json=data)
    print("Respuesta del servidor:", response.json())

def receive_messages():
    global server_url
    global identifier
    receive_url = server_url.replace("/send_message", "/receive_messages")
    params = {"user": identifier}  # identifier es tu ID o nombre de usuario
    response = requests.get(receive_url, params=params)
    messages_list = response.json()
    if not messages_list:
        print("No hay mensajes nuevos.")
        return
    for msg_pair in messages_list:
        msg_hex, sender = msg_pair
        encrypted_msg_bytes = bytes.fromhex(msg_hex)
        msg = decrypt_messages(encrypted_msg_bytes, sender)
        print(f"Mensaje de {sender}: {msg}")


def decrypt_messages(message, sender):
    global external_public_key
    try: 
        external_public_key = PublicKey(contacts[sender])
    except:
        print("No tienes ese contacto")
        return
    box = Box(private_key, external_public_key)
    decrypted_message = box.decrypt(message)
    message = decrypted_message.decode()
    return message

def encrypt_message():
    global external_public_key
    global message
    global private_key
    global public_key
    global box
    global encrypted_message
    try: 
        external_public_key = PublicKey(contacts[receiver])
    except:
        print("No tienes ese contacto")
    box = Box(private_key, external_public_key)
    encrypted_message = box.encrypt(message.encode())

def main():
    global message
    global receiver
    global public_key
    global private_key
    if not private_key_file.exists() or not public_key_file.exists():
        gen_keys()
    else:
        with open("private_key", "rb") as f:
            private_key = PrivateKey(f.read())
            print(f"Clave privada = {private_key}")
        with open("public_key", "rb") as f:
            public_key = PublicKey(f.read())
            print(f"Clave pública = {public_key}")
    message = input("Mensaje a enviar: ")
    receiver = input("Mensaje para: ")
    encrypt_message()
    send_message()
    while True:
        receive_messages()
        time.sleep(2)
def comprobations():
    try:
        with open("public_key", "r") as f:
            pass
    except:
        print("No tienes clave, generando...")
        gen_keys()
    try:
        with open("identifier", "r") as f:
            identifier = f.read().strip()
    except:
        gen_id()
    try:
        global contacts
        with open("contacts.pkl", "rb") as f:
            contacts = pickle.load(f)
        with open("contacts.pkl", "rb") as f:
            contacts = pickle.load(f)
    except:
        print("No hay contactos, añadelos")
        add_contact()


comprobations()
ToDo = int(input("Que quieres: dar clave, añadir contacto, enviar mensaje(0, 1, 2)"))
if ToDo == 0:
    give_information()
if ToDo == 1:
    add_contact()
if ToDo == 2:
    main()
