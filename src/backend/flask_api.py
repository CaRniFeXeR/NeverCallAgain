import io
from pathlib import Path
from flask import Flask, request, Response, jsonify, send_from_directory
import flask
import numpy as np
import sounddevice as sd
import queue
import os
from wav_handler import get_wave_header, split_wave_bytes_into_chunks
from chatgpt import ChatGPT
from TtS import TextToSpeech
import time

# from src.backend.chatgpt import ChatGPT
# from src.backend.TtS import TextToSpeech

app = Flask(__name__, static_folder="./../frontend")

# Create a byte stream
# output_stream = io.BytesIO()
data_queue = queue.Queue()
app.writing_data = False

tts = TextToSpeech()


@app.route('/stream_mp3')
def stream_mp3():
    def gen():
        with open('german_speech1.wav', 'rb') as f:
            data = f.read(1024)
            while data:
                yield data
                data = f.read(1024)
                # output_stream.write(data)

    return Response(gen(), mimetype='audio/x-wav')


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


@app.route('/stream_audio')
def stream_audio():
    return Response(generate_audio(),
                    mimetype='audio/x-wav')


@app.route('/record_audio', methods=['POST'])
def record_audio():
    audio_data = request.data
    sd.play(audio_data, 44100)
    return 'OK'


@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    text_input = data['text_input']
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

    response = {'message': 'Data received successfully'}
    return jsonify(response)


@app.route('/static/<path:filename>')
def return_client_files(filename: str):
    return send_from_directory("./../frontend", filename)


@app.route('/')
def index():
    """ Displays the index page accessible at '/'
    """
    print(app.instance_path)
    return flask.send_file('./../frontend/index.html')


if __name__ == '__main__':
    app.run(host=os.environ.get("FLASK_HOST_IP", "localhost"))
