# flask_server.py
from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

# Global variables to track readiness, data exchange, and communication state
notebook1_ready = False
notebook2_ready = False
received_array = None
notebook1_message = None
notebook2_message = None
channel_open = True


@app.route('/notebook1_ready', methods=['POST'])
def notebook1_ready_status():
    global notebook1_ready
    notebook1_ready = True
    return jsonify({"status": "Notebook 1 ready", "notebook2_ready": notebook2_ready})


@app.route('/notebook2_ready', methods=['POST'])
def notebook2_ready_status():
    global notebook2_ready
    notebook2_ready = True
    return jsonify({"status": "Notebook 2 ready", "notebook1_ready": notebook1_ready})


@app.route('/status', methods=['GET'])
def check_status():
    return jsonify({"notebook1_ready": notebook1_ready, "notebook2_ready": notebook2_ready})


@app.route('/send_array', methods=['POST'])
def receive_array():
    global received_array
    data = request.get_json()
    received_array = np.array(data["array"])  # Convert list to NumPy array
    return jsonify({"status": "Array received", "received_array_shape": received_array.shape})


@app.route('/check_array', methods=['GET'])
def check_array():
    if received_array is not None:
        return jsonify({"status": "Array exists", "shape": received_array.shape})
    else:
        return jsonify({"status": "No array received"})


@app.route('/send_message', methods=['POST'])
def receive_message():
    global notebook1_message, notebook2_message, channel_open, notebook1_ready, notebook2_ready
    data = request.get_json()
    sender = data.get("sender")
    message = data.get("message")

    if sender == "notebook1":
        notebook1_message = message
        if message == 'END':
            notebook1_ready = False
    elif sender == "notebook2":
        notebook2_message = message
        if message == 'END':
            notebook2_ready = False

    if message == "END":
        channel_open = False
        return jsonify({"status": "Channel closed"})

    return jsonify({"status": "Message received", "message": message})


@app.route('/receive_message', methods=['GET'])
def send_message():
    global notebook1_message, notebook2_message
    requester = request.args.get("requester")

    if requester == "notebook1" and notebook2_message:
        msg = notebook2_message
        notebook2_message = None  # Clear the message after sending
        return jsonify({"message": msg})

    if requester == "notebook2" and notebook1_message:
        msg = notebook1_message
        notebook1_message = None  # Clear the message after sending
        return jsonify({"message": msg})

    return jsonify({"message": None})


@app.route('/check_channel', methods=['GET'])
def check_channel():
    return jsonify({"channel_open": channel_open})


if __name__ == '__main__':
    app.run(debug=True)
