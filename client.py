import nacl.utils
import subprocess
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
        print(f"\n Tu clave pública es: {hex_public_key}, dásela a otros para que te añadan a sus contactos")

def see_contacts():
    print("TODOS LOS CONTACTOS\n----------------------")
    i = 1
    for contact in contacts:
        print(f"{i}. Nombre: {contact}, Clave: {contacts[contact].hex()}\n")
        i += 1

def add_contact():
    global contacts
    try: 
        with open("contacts.json", "r") as f:
            see_contacts()
            hex_contacts = json.load(f)
            for name, hex_key in hex_contacts.items():
                contacts[name] = bytes.fromhex(hex_key)
    except:
        contacts = {}
    identifier = input("Identificador del contacto: ")
    hex_public_key = input("Hexadecimal del contacto: ")
    public_key = bytes.fromhex(hex_public_key)
    contacts[identifier] = public_key
    with open("contacts.json", mode="w", encoding="utf-8") as f:
        hex_contacts = {}
        for contact in contacts:
            hex_contact = contacts[contact].hex()
            hex_contacts[contact] = hex_contact
        json.dump(hex_contacts, f)
    see_contacts()



def send_message():
    global identifier
    message = input("Mensaje a enviar: ")
    receiver = input("Entregar a: ")
    encrypted_message = encrypt_message(message, receiver)
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
        print(contacts.get(receiver))
        return None
    print(f"type(private_key)={type(private_key)}, type(contacts[receiver])={type(contacts[receiver])}")
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
    global private_key
    global public_key
    try:
        with open("private_key", "rb") as f:
            private_key = PrivateKey(f.read())
        with open("public_key", "rb") as f:
            public_key = PublicKey(f.read())
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

def menu():
    ToDo = int(input("\nQue quieres:\n 0. Dar tu clave\n 1. Añadir contacto\n 2. Ver contactos\n 3. Enviar mensaje\n 4. Ver mensajes nuevos\n 5. Salir\n"))
    if ToDo == 0:
        subprocess.run("clear", shell = True, executable="/bin/bash")
        give_information()
    if ToDo == 1:
        subprocess.run("clear", shell = True, executable="/bin/bash")
        add_contact()
    if ToDo == 2:
        subprocess.run("clear", shell = True, executable="/bin/bash")
        see_contacts()
    if ToDo == 3:
        subprocess.run("clear", shell = True, executable="/bin/bash")
        send_message()  
    if ToDo == 4:
        subprocess.run("clear", shell = True, executable="/bin/bash")
        receive_messages()
    if ToDo == 5:
        subprocess.run("clear", shell = True, executable="/bin/bash")
        return "break"
    

comprobations()
while True:
    comprobations()
    if menu() == "break":
        break
