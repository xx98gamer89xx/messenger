from flask import Flask, request, jsonify


app = Flask(__name__)
messages = {}

@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.json
    receiver = data['to']
    sender = data["from"]
    message = data['message']
    messages.setdefault(receiver, []).append([message, sender])
    print(f"El mensaje va a {data["from"]}, contiene {data["message"]} y hacia {data["to"]}")
    return jsonify({"status": "ok"})
@app.route("/receive_messages", methods=["GET"])
def receive_messages():
    user = request.args.get('user')
    msgs = messages.get(user, [])
    messages[user] = []
    return jsonify(msgs)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)