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
from TtS import TextToSpeech
from voice_handler import VoiceHandler
from wav_handler import get_wave_header, split_wave_bytes_into_chunks

# from src.backend.chatgpt import ChatGPT
# from src.backend.TtS import TextToSpeech

app = Flask(__name__, static_folder="./../frontend")

# Create a byte stream
# output_stream = io.BytesIO()
data_queue = queue.Queue()
app.writing_data = False

tts = TextToSpeech() 


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


@app.route("/recieve_audio_input")
def recieve_audio_input(data):
    # Convert the audio data to a numpy array
    audio = np.frombuffer(data, dtype=np.float32)


@app.route("/audio", methods=["POST"])
def handle_audio_stream():
    # Get the content type and length of the incoming request
    content_type = request.headers.get("Content-Type")
    content_length = int(request.headers.get("Content-Length"))

    # Check that the request is for audio data
    if content_type == "audio/raw" and content_length > 0:
        # Open a stream to read the incoming audio data
        audio_stream = request.stream

        # Process the audio data in real-time
        voicehandler = VoiceHandler()
        voicehandler.handle_input_stream(audio_stream)

        # Return a response to the client
        return "Audio data received"

    # If the request is not for audio data, return an error response
    else:
        return "Invalid request", 400


if __name__ == "__main__":
    app.run(host=os.environ.get("FLASK_HOST_IP", "localhost"))
