# flask_server.py
from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

# Global variables to track readiness, data exchange, and communication state
m_ready = False
n_ready = False
coordinates = None
location = None
response = None
channel_open = True


@app.route('/', methods=['GET'])
def basic():
    pass

@app.route('/microscope_ready', methods=['POST'])
def microscope_ready():
    global m_ready, n_ready
    m_ready = True
    return jsonify({'microscope': m_ready, 'notebook': n_ready})


@app.route('/notebook_ready', methods=['POST'])
def notebook_ready():
    global m_ready, n_ready
    n_ready = True
    return jsonify({'microscope': m_ready, 'notebook': n_ready})

@app.route('/microscope_stop', methods=['POST'])
def microscope_stop():
    global m_ready, n_ready
    m_ready = False
    return jsonify({'microscope': m_ready, 'notebook': n_ready})


@app.route('/notebook_stop', methods=['POST'])
def notebook_stop():
    global m_ready, n_ready
    n_ready = False
    return jsonify({'microscope': m_ready, 'notebook': n_ready})


@app.route('/status', methods=['GET'])
def check_status():
    global m_ready, n_ready
    return jsonify({'microscope': m_ready, 'notebook': n_ready})

@app.route('/send_coordinates', methods=['POST'])
def receive_array():
    global coordinates, n_ready
    data = request.get_json()
    coordinates = data["coordinates"]  # Convert list to NumPy array
    n_ready = False
    return jsonify({'status': "Coordinates uploaded", 'received_array_shape': coordinates.shape})

@app.route('/get_coordinates', methods=['GET'])
def send_coordinates():
    global n_ready, coordinates
    if coordinates is not None:
        coord = coordinates
        n_ready = True
        return jsonify({"status": "Coordinates sent", "coordinates": coord})
    else:
        return jsonify({"status": "None", "coordinates": []})

@app.route('/check_coordinates', methods=['GET'])
def check_coordinates():
    if coordinates is not None:
        return jsonify({"status": "Coordinates exists", "shape": coordinates.shape})
    else:
        return jsonify({"status": "No coordinates received"})

@app.route('/send_message', methods=['POST'])
def receive_message():
    global location, response, m_ready, n_ready
    data = request.get_json()
    sender = data.get("sender")
    message = data.get("data")

    if sender == "microscope":
        response = message
        n_ready = False
        if message == 'END':
            m_ready = False
    elif sender == "notebook":
        location = message
        m_ready = False
        if message == 'END':
            n_ready = False

    return jsonify({"status": "Message received", "message": message})


@app.route('/get_message', methods=['GET'])
def send_message():
    global location, response, m_ready, n_ready
    requester = request.args.get("requester")

    if requester == "microscope" and location:
        msg = location
        location = None  # Clear the message after sending
        m_ready = True
        return jsonify({"reponse": msg})

    if requester == "notebook" and response:
        msg = response
        response = None  # Clear the message after sending
        n_ready = True
        return jsonify({"location": msg})

    return jsonify({"message": None})


if __name__ == '__main__':
    app.run(debug=False)
