from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
sql_table_messages = ""

def write_database(to, message, sender):
    with sqlite3.connect("sqlite.db") as connection:
        cursor = connection.cursor()
        cursor.execute(""" CREATE TABLE IF NOT EXISTS messages (
        for text,
        message text,
        sender text
        )
        """)
        cursor.execute("INSERT INTO messages VALUES (?, ?, ?)", (to, message, sender))
        ## Hacer los cambios
        connection.commit()

def delete_message(to, message, sender):
    with sqlite3.connect("sqlite.db") as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE from messages WHERE for=? AND message=? AND sender=?", (to, message, sender))
        ## Hacer los cambios
        connection.commit()

def find_messages_to_send(to):
    msgs = []
    data = load_database()
    for row in data:
        # Si el nombre de a quien van los mensajes coincide con cuales queremos, entregamos los mensajes
        if row[0] == to:
            msgs.append((row[1], row[2]))
            delete_message(row[0], row[1], row[2])
        else:
            pass
    return msgs



def load_database():
    with sqlite3.connect("sqlite.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM messages")
        return cursor.fetchall()
    


@app.route("/send_message", methods=["POST"])
# Estructura del diccionario
#    messages = {
#    "1": [
#        ["hola", "0"],        # mensaje de "0" a "1"
#        ["qué tal", "2"]      # mensaje de "2" a "1"
#    ],
#    "2": [
#        ["buenos días", "0"]  # mensaje de "0" a "2"
#    ],
#    "3": []                   # no tiene mensajes todavía
#    }

def send_message():
    data = request.json
    receiver = data['to']
    sender = data["from"]
    message = data['message']
    write_database(receiver, message, sender)
    print(f"El mensaje va desde {data["from"]}, contiene {data["message"]}, hacia {data["to"]}")
    return jsonify({"status": "ok"})
@app.route("/receive_messages", methods=["GET"])
def receive_messages():
    user = request.args.get('user')
    msgs = find_messages_to_send(user)
    return jsonify(msgs)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)