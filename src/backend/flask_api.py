import io
from pathlib import Path
from flask import Flask, request, Response, jsonify, send_from_directory
import flask
import numpy as np
import sounddevice as sd
import queue
from src.backend.wav_handler import get_wave_header
from .chatgpt import ChatGPT
from .TtS import TextToSpeech
import time
# from src.backend.chatgpt import ChatGPT
# from src.backend.TtS import TextToSpeech

app = Flask(__name__, static_folder="./../frontend")

# Create a byte stream
output_stream = io.BytesIO()
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
        if not app.writing_data and data_queue.empty():
                    time.sleep(2) #lol hack
        while not data_queue.empty():
                data = data_queue.get()
                yield data
                if app.writing_data and data_queue.empty():
                    time.sleep(2) #lol hack
        # seek_idx = 0
        # with open('generate_audio.wav', 'wb') as f:
            
            # output_stream.seek(seek_idx)
            # data = output_stream.read(1024)
            # while data:
            #     yield data
            #     f.write(data)
            #     seek_idx += 1024
            #     output_stream.seek(seek_idx)
            #     data = output_stream.read(1024)
        
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
    output_stream.write(get_wave_header())
    app.writing_data = True
    data_queue.put(get_wave_header())
    for delta in chatgpt.get_response_by_delimiter(text_input):
        audio_segment = tts.text_to_speech_numpy_pmc(delta)
        print(delta)
        bytes = audio_segment.tobytes()
        output_stream.seek(0,io.SEEK_END)
        output_stream.write(bytes)
        data_queue.put(bytes)
    # print(result)
    # output_stream.close()bytes
    app.writing_data = False
 
    response = {'message': 'Data received successfully'}
    return jsonify(response)

@app.route('/static/<path:filename>')
def return_client_files(filename : str):
    return send_from_directory("./../frontend", filename)

@app.route('/')
def index():
    """ Displays the index page accessible at '/'
    """
    print(app.instance_path)
    return flask.send_file('./../frontend/index.html')


if __name__ == '__main__':
    app.run(host="172.21.146.137")