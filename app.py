# flask_server.py
from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

# Global variables to track readiness, data exchange, and communication state
microscope_ready = False
notebook_ready = False
coordinates = None
location = None
response = None
channel_open = True


@app.route('/microscope_ready', methods=['POST'])
def microscope_ready():
    global microscope_ready
    microscope_ready = True
    return jsonify({"microscope": microscope_ready, "notebook": notebook_ready})


@app.route('/notebook_ready', methods=['POST'])
def notebook_ready():
    global notebook_ready
    notebook_ready = True
    return jsonify({"microscope": microscope_ready, "notebook": notebook_ready})

@app.route('/microscope_ready', methods=['POST'])
def microscope_stop():
    global microscope_ready
    microscope_ready = False
    return jsonify({"microscope": microscope_ready, "notebook": notebook_ready})


@app.route('/notebook_ready', methods=['POST'])
def notebook_stop():
    global notebook_ready
    notebook_ready = False
    return jsonify({"microscope": microscope_ready, "notebook": notebook_ready})


@app.route('/status', methods=['GET'])
def check_status():
    return jsonify({"microscope": microscope_ready, "notebook": notebook_ready})

@app.route('/send_coordinates', methods=['POST'])
def receive_array():
    global coordinates, notebook_ready
    data = request.get_json()
    coordinates = np.array(data["coordinates"])  # Convert list to NumPy array
    notebook_ready = False
    return jsonify({"status": "Coordinates uploaded", "received_array_shape": coordinates.shape})

@app.route('/get_coordinates', methods=['POST'])
def send_coordinates():
    global notebook_ready
    if coordinates is not None:
        coord = coordinates
        notebook_ready = True
        return jsonify({"status": "Coordinates sent", "coordinates": coord})

@app.route('/check_coordinates', methods=['GET'])
def check_coordinates():
    if coordinates is not None:
        return jsonify({"status": "Coordinates exists", "shape": coordinates.shape})
    else:
        return jsonify({"status": "No coordinates received"})

@app.route('/send_message', methods=['POST'])
def receive_message():
    global location, response, microscope_ready, notebook_ready
    data = request.get_json()
    sender = data.get("sender")
    message = data.get("data")

    if sender == "microscope":
        response = message
        notebook_ready = False
        if message == 'END':
            microscope_ready = False
    elif sender == "notebook":
        location = message
        microscope_ready = False
        if message == 'END':
            notebook_ready = False

    return jsonify({"status": "Message received", "message": message})


@app.route('/receive_message', methods=['GET'])
def send_message():
    global location, response, microscope_ready, notebook_ready
    requester = request.args.get("requester")

    if requester == "microscope" and location:
        msg = location
        location = None  # Clear the message after sending
        microscope_ready = True
        return jsonify({"reponse": msg})

    if requester == "notebook" and response:
        msg = response
        response = None  # Clear the message after sending
        notebook_ready = True
        return jsonify({"location": msg})

    return jsonify({"message": None})


if __name__ == '__main__':
    app.run(debug=False)
