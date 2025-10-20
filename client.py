import nacl.utils
import requests
import time
import json
from flask import Flask, request, jsonify
from nacl.public import PrivateKey, PublicKey, Box
from pathlib import Path
identifier = 0
server_url = "http://127.0.0.1:5000/send_message"
private_key_file = Path("private_key")
public_key_file = Path("public_key")
contacts = {}
private_key = None
public_key = None
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
    with open(public_key_file, "rb") as f:
        binary_public_key = f.read()
        hex_public_key = binary_public_key.hex()
        print(hex_public_key)

def add_contact():
    global contacts
    with open("contacts.json", "r") as f:
        hex_contacts = json.load(f)
        print(hex_contacts)
        for i in range(len(hex_contacts)):
            contact_id = contacts.get(i)
            contacts[contact_id] = bytes.fromhex(contacts[contact_id])
            print(f"Contacto {str(i)} añadido: {contacts[i]}")
            i += 1
        print(contacts)
    identifier = input("Identificador del contacto: ")
    hex_public_key = input("Hexadecimal del contacto: ")
    public_key = bytes.fromhex(hex_public_key)
    contacts[identifier] = public_key
    for contact in contacts:
        contacts[contact] = contacts[contact].hex()
    with open("contacts.json", mode="w", encoding="utf-8") as f:
        json.dump(contacts, f)



def send_message(receiver, encrypted_message):
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
    try: 
        external_public_key = PublicKey(contacts[sender])
    except:
        print("No tienes ese contacto")
        return
    box = Box(private_key, external_public_key)
    decrypted_message = box.decrypt(message)
    message = decrypted_message.decode()
    return message

def encrypt_message(message, receiver):
    try:
        external_public_key = PublicKey(contacts.get(receiver))
    except:
        print("No tienes ese contacto")
        return None
    box = Box(private_key, external_public_key)
    encrypted_message = box.encrypt(message.encode())
    return encrypted_message

def main(): 
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
    encrypted_message = encrypt_message(message, receiver)
    send_message(receiver, encrypted_message)
    while True:
        receive_messages()
        time.sleep(2)

def comprobations():
    global contacts
    global identifier
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
        with open("contacts.json", "r") as f:
            hex_contacts = json.load(f)
            contacts = {identifier: bytes.fromhex(hex_key) for identifier, hex_key in hex_contacts.items()}
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
