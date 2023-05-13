import io
import os
import queue
import time
from pathlib import Path

import flask
import numpy as np
import sounddevice as sd
from chatgpt import ChatGPT
from flask import Flask, Response, jsonify, request, send_from_directory
# from flask_socketio import SocketIO
# from flask_sockets import Sockets
from flask_sock import Sock
from TtS import TextToSpeech
from voice_handler import VoiceHandler
from wav_handler import get_wave_header, split_wave_bytes_into_chunks

# from src.backend.chatgpt import ChatGPT
# from src.backend.TtS import TextToSpeech

app = Flask(__name__, static_folder="./../frontend")
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 30}

sockets = Sock(app)

# Create a byte stream
# output_stream = io.BytesIO()
data_queue = queue.Queue()
app.writing_data = False

tts = TextToSpeech() 
voice_handler = VoiceHandler()


def generate_audio():
    print("generate_audio")
    time.sleep(1)
    if not app.writing_data and data_queue.empty():
        time.sleep(1)  # lol hack
    while app.writing_data or not data_queue.empty():
        if not data_queue.empty():
            data = data_queue.get()
            yield data
        if app.writing_data and data_queue.empty():
            time.sleep(1)  # lol hack

    print("finished gen audio")


@app.route("/stream_audio")
def stream_audio():
    return Response(generate_audio(), mimetype="audio/x-wav")


@app.route("/record_audio", methods=["POST"])
def record_audio():
    audio_data = request.data
    sd.play(audio_data, 44100)
    return "OK"


@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    text_input = data["text_input"]
    chatgpt = ChatGPT()
    # output_stream.write(get_wave_header())
    app.writing_data = True
    data_queue.put(get_wave_header())
    for delta in chatgpt.get_response_by_delimiter(text_input):
        audio_segment = tts.text_to_speech_numpy_pmc(delta)
        print(delta)
        bytes = audio_segment.tobytes()

        for byte_chunk in split_wave_bytes_into_chunks(bytes):
            data_queue.put(byte_chunk)
    # print(result)
    # output_stream.close()bytes
    app.writing_data = False

    response = {"message": "Data received successfully"}
    return jsonify(response)


@app.route("/static/<path:filename>")
def return_client_files(filename: str):
    return send_from_directory("./../frontend", filename)


@app.route("/")
def index():
    """Displays the index page accessible at '/'"""
    print(app.instance_path)
    return flask.send_file("./../frontend/index.html")


@app.route("/recieve_audio2", methods=["POST"])
def recieve_audio2():
    """Displays the index page accessible at '/'"""

    print("reciving data")
    data = request.data

    data = get_wave_header(sample_rate=16000) + data

    voice_handler.handle_input_byte_string(data)

    with open("output.wav","wb") as f:
        f.write(data)

    response = jsonify("File received and saved!")
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@app.route("/recieve_audio", methods=["POST"])
def recieve_audio():
    """Displays the index page accessible at '/'"""
    files = request.files
    file = files.get('file')
    content = file.read()


    with open('test.webm', 'wb') as f:
        f.write(content)

    voice_handler.handle_input_byte_string(content)

    response = jsonify("File received and saved!")
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@sockets.route("/recieve_audio_input")
def handle_audio_stream(ws):
    print("reciving audio..")
    while not ws.connected:
        recieved_audio = ws.receive()
        print("recieved audio")
        print(recieved_audio)
        voice_handler.handle_input_stream(recieved_audio)
    


if __name__ == "__main__":
    app.run(host=os.environ.get("FLASK_HOST_IP", "localhost"))
    # from gevent import pywsgi
    # from geventwebsocket.handler import WebSocketHandler
    # server = pywsgi.WSGIServer((os.environ.get("FLASK_HOST_IP", "localhost"), 5000), app, handler_class=WebSocketHandler)
    # server.serve_forever()
