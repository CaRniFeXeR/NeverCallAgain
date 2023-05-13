import io
import os
import queue
import time
from pathlib import Path

import flask
import numpy as np
import sounddevice as sd
from backend.chunk_handler import ChunkHandler
from backend.conversation_handler import ConversationHandler
from chatgpt import ChatGPT
from flask import Flask, Response, jsonify, request, send_from_directory
# from flask_socketio import SocketIO
# from flask_sockets import Sockets
from flask_sock import Sock
from TtS import TextToSpeech
from voice_handler import VoiceHandler
from wav_handler import get_empty_wave_bytes, get_wave_header, split_wave_bytes_into_chunks

# from src.backend.chatgpt import ChatGPT
# from src.backend.TtS import TextToSpeech

app = Flask(__name__, static_folder="./../frontend")
# app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 30}
# sockets = Sock(app)

# Create a byte stream
# output_stream = io.BytesIO()
data_queue = queue.Queue()
app.writing_data = False

tts = TextToSpeech() 
voice_handler = VoiceHandler()
chunk_handler = ChunkHandler()
chatgpt = ChatGPT()
conv_handler = ConversationHandler()


def write_to_queue(bytes):
    for byte_chunk in split_wave_bytes_into_chunks(bytes):
        data_queue.put(byte_chunk)


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
    # output_stream.write(get_wave_header())
    app.writing_data = True
    data_queue.put(get_wave_header())
    for delta in chatgpt.get_response_by_delimiter(text_input):
        audio_segment = tts.text_to_speech_numpy_pmc(delta)
        print(delta)
        bytes = audio_segment.tobytes()

        write_to_queue(bytes)
    # print(result)
    # output_stream.close()bytes
    app.writing_data = False

    response = {"message": "Data received successfully"}
    return jsonify(response)

@app.route("/start_call", methods=["POST"])
def start_call():
    chunk_handler.start_call()
    opener_text = "Hallo ich möchte gerne einen Termin für Florian Pfiel ausmachen. Haben Sie nächsten Donnerstag um 9:30 Uhr zeit?"
    conv_handler.append_initiator_text(opener_text)

    audio_segment = tts.text_to_speech_numpy_pmc(opener_text)
    # print(delta)
    bytes = audio_segment.tobytes()

    write_to_queue(bytes)


@app.route("/static/<path:filename>")
def return_client_files(filename: str):
    return send_from_directory("./../frontend", filename)


@app.route("/")
def index():
    """Displays the index page accessible at '/'"""
    print(app.instance_path)
    return flask.send_file("./../frontend/index.html")


@app.route("/recieve_audio", methods=["POST"])
def recieve_audio():
    """Displays the index page accessible at '/'"""

    print("reciving data")
    data = request.data

    data = get_wave_header(sample_rate=16000) + data
    data_np = np.array(data, dtype=np.int32)

    # voice_handler.handle_input_byte_string(data)

    # chunk_handler.handle_input_byte_string(data)
    data_processed, can_speak = chunk_handler.process_chunk(data_np)

    if chunk_handler.state_machine.state == "waiting_in_queue":
        print("waiting in queue")
    elif chunk_handler.state_machine.state == "start_opener_speaking":
        
        #moved to /start_call for now ..
        chunk_handler.transition_to_wait()
    elif chunk_handler.state_machine.state == "start_speaking":
         
        last_answer = conv_handler._receiver_text[-1]

        for delta in chatgpt.get_response_by_delimiter(last_answer):
            audio_segment = tts.text_to_speech_numpy_pmc(delta)
            print(delta)
            bytes = audio_segment.tobytes()
            write_to_queue(bytes)
        
        chunk_handler.transition_to_wait()
        
    elif chunk_handler.state_machine.state == "speaking":
        print("still speaking")
        n_chunks = data_np.shape[0] // 1024
        write_to_queue(get_empty_wave_bytes(header=False,n_chunks=n_chunks))


    elif chunk_handler.state_machine.state == "waiting":
        #listen to input
        print("waiting")
        transcript = voice_handler.handle_input_byte_string(data)
        conv_handler.append_receiver_text(transcript)
        n_chunks = data_np.shape[0] // 1024
        write_to_queue(get_empty_wave_bytes(header=False,n_chunks=n_chunks))


    
    # if chunk_handler.state_machine.state == "":

    # with open("output.wav","wb") as f:
    #     f.write(data)

    response = jsonify("File received and saved!")
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@app.route("/recieve_audio_old", methods=["POST"])
def recieve_audio_old():
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


if __name__ == "__main__":
    app.run(host=os.environ.get("FLASK_HOST_IP", "localhost"))