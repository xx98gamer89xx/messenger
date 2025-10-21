import nacl.utils
import subprocess
import requests
import time
import json
import sqlite3
from nacl.public import PrivateKey, PublicKey, Box

identifier = 0
contacts = {}
private_key = None
public_key = None

# ------------------ PARTE DE TOR  -------------------
server_url = "http://g6byxwj63dqhjeknwhstgyd3lbe5gzda6zv6scway6r4mtyvm2wdvhyd.onion/send_message"  # Dirección del servidor de tor
proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}
    
# ------------------ LLAVES Y NOMBRE ------------------

def gen_keys():
    global private_key, public_key
    private_key = PrivateKey.generate()
    public_key = private_key.public_key
    with open("private_key", "wb") as f:
        f.write(private_key.encode())
    with open("public_key", "wb") as f:
        f.write(public_key.encode())
    give_information()

def gen_id():
    global identifier
    identifier = input("No tienes nombre, póntelo: ")
    with open("identifier", "w") as f:
        f.write(identifier)

def give_information():
    with open("public_key", "rb") as f:
        binary_public_key = f.read()
        hex_public_key = binary_public_key.hex()
        print(f"\nTu clave pública es: {hex_public_key}, dásela a otros para que te añadan a sus contactos")

# ------------------ CONTACTOS ------------------

def see_contacts(text):
    print(f"{text}\n----------------------")
    with open("contacts.json", mode="r", encoding="utf-8") as f:
        hex_contacts = json.load(f)
        i = 0
        for key in hex_contacts.keys():
            i += 1
            print(f"{i}. Nombre: {key} Clave: {hex_contacts[key]}")

def add_contact():
    global contacts
    try:
        # Carga el archivo de contactos a la variable y lo traduce a bytes, para que sea operable por nacl
        with open("contacts.json", "r") as f:
            see_contacts("TODOS LOS CONTACTOS")
            hex_contacts = json.load(f)
            for name, hex_key in hex_contacts.items():
                contacts[name] = bytes.fromhex(hex_key)
    except FileNotFoundError as e:
        # Si no hay archivo, considera que contacts está vacío
        contacts = {}
        print(e)
    # Pide credenciales del contacto, las mete a la variable y las pasa al json
    identifier = input("Identificador del contacto: ")
    hex_public_key = input("Hexadecimal del contacto: ")
    public_key = bytes.fromhex(hex_public_key)
    contacts[identifier] = public_key
    text = "NUEVOS CONTACTOS"
    with open("contacts.json", "w", encoding="utf-8") as f:
        hex_contacts = {c: contacts[c].hex() for c in contacts}
        json.dump(hex_contacts, f)
    see_contacts(text)

# ------------------ BASE DE DATOS ------------------

def write_database(message, sender):
    with sqlite3.connect("sqlite.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS messages (
            message text,
            sender text
        )""")
        cursor.execute("INSERT INTO messages VALUES (?, ?)", (message, sender))
        conn.commit()

def load_database():
    with sqlite3.connect("sqlite.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM messages")
        return cursor.fetchall()

# ------------------ ENVIAR Y RECIBIR ------------------

def send_message():
    global identifier
    message = input("Mensaje a enviar: ")
    receiver = input("Entregar a: ")
    encrypted_message = encrypt_message(message, receiver)
    data = {"to": receiver, "message": encrypted_message.hex(), "from": identifier}
    try:
        # Manda mensajes y el servidor responde si todo ok
        response = requests.post(server_url, json=data, timeout=10, proxies=proxies)
        print("Mensaje enviado correctamente")
    except Exception as e:
        print("Error al enviar mensaje:", e)

def receive_messages():
    receive_url = server_url.replace("/send_message", "/receive_messages")
    params = {"user": identifier}
    try:
        # Recibe mensajes del servidor destinados a él
        response = requests.get(receive_url, params=params, timeout=10, proxies=proxies)
        messages_list = response.json()
        for msg_hex, sender in messages_list:
            write_database(msg_hex, sender)
    except Exception as e:
        print("Error al recibir mensajes:", e)

# ------------------ MENSAJES ------------------

def load_messages():
    # Mete en memoria los mensajes de la base de datos sin filtro (los mensajes de todos los usuarios) y los envía
    messages = []
    for row in load_database():
        hex_message, sender = row
        message_bytes = bytes.fromhex(hex_message)
        messages.append(decrypt_messages(message_bytes, sender))
    return messages

def select_message():
    # Selecciona los mensajes que son del contacto y se los manda a read_message()
    messages = load_messages()
    unique_senders = list({sender for _, sender in messages})
    print("Tienes mensajes de esta gente: ")
    for i, sender in enumerate(unique_senders):
        print(f"{i + 1}. {sender}")
    indice = int(input("Cual quieres leer: ")) -1
    wanted_sender = unique_senders[indice]
    read_message(messages, wanted_sender)

def read_message(messages, objective):
    # Escribe los mensajes que le pasan
    for message, sender in messages:
        if sender == objective:
            print(f"-> {message}")

# ------------------ CIFRADO ------------------

def decrypt_messages(message, sender):
    # Desencripta mensajes si tiene el contacto y la clave
    try: 
        external_public_key = PublicKey(contacts[sender])
    except:
        print("No tienes ese contacto")
        return "", ""
    box = Box(private_key, external_public_key)
    decrypted_message = box.decrypt(message)
    return decrypted_message.decode(), sender

def encrypt_message(message, receiver):
    # Encripta mensajes con la clave del destinatario (receiver)
    try:
        external_public_key = PublicKey(contacts.get(receiver))
    except:
        print("No tienes ese contacto")
        return None
    box = Box(private_key, external_public_key)
    return box.encrypt(message.encode())

# ------------------ INICIALIZACIÓN ------------------

def comprobations():
    # Comprueba si hay contactos, id, claves y si no los crea
    global contacts, identifier, private_key, public_key
    try:
        with open("private_key", "rb") as f:
            private_key = PrivateKey(f.read())
        with open("public_key", "rb") as f:
            public_key = PublicKey(f.read())
    except:
        gen_keys()
    try:
        with open("identifier", "r") as f:
            identifier = f.read().strip()
    except:
        gen_id()
    try:
        with open("contacts.json", "r") as f:
            hex_contacts = json.load(f)
            contacts = {name: bytes.fromhex(k) for name, k in hex_contacts.items()}
    except:
        add_contact()

# ------------------ MENÚ ------------------

def menu():
    # Actúa como TUI, permite al usuario seleccionar que quiere hacer
    ToDo = int(input("\nQue quieres:\n 0. Dar tu clave\n 1. Añadir contacto\n 2. Ver contactos\n 3. Enviar mensaje\n 4. Ver mensajes nuevos\n 5. Salir\n"))
    if ToDo == 0:
        subprocess.run("clear", shell=True, executable="/bin/bash")
        give_information()
    elif ToDo == 1:
        subprocess.run("clear", shell=True, executable="/bin/bash")
        add_contact()
    elif ToDo == 2:
        subprocess.run("clear", shell=True, executable="/bin/bash")
        see_contacts("TODOS LOS CONTACTOS")
    elif ToDo == 3:
        subprocess.run("clear", shell=True, executable="/bin/bash")
        send_message()
    elif ToDo == 4:
        subprocess.run("clear", shell=True, executable="/bin/bash")
        receive_messages()
        select_message()
    elif ToDo == 5:
        return "break"

# ------------------ EJECUCIÓN ------------------
comprobations()
while True:
    # Ejecuta menú cada vez que se completa una tarea de ToDo y si se pide salir rompe el bucle
    if menu() == "break":
        break