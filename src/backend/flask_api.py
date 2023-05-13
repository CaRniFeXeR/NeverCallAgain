import io
import os
import queue
import time
from pathlib import Path

import flask
import numpy as np
import sounddevice as sd
from chunk_handler import ChunkHandler
from conversation_handler import ConversationHandler
from chatgpt import ChatGPT
from flask import Flask, Response, jsonify, request, send_from_directory
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
    print("write_to_queue")
    for byte_chunk in split_wave_bytes_into_chunks(bytes):
        data_queue.put(byte_chunk)


def generate_audio():
    print("generate_audio")
    stream_count = 0
    # time.sleep(1)
    if not app.writing_data and data_queue.empty():
        time.sleep(1)  # lol hack
    while app.writing_data or not data_queue.empty():
        if not data_queue.empty():
            data = data_queue.get()
            yield data
            stream_count += 1
            print(f"streaming audio back {stream_count}")
        if app.writing_data and data_queue.empty():
            time.sleep(3)  # lol hack
            print("wating for new data to stream")

    print("finished gen audio")


@app.route("/stream_audio")
def stream_audio():
    return Response(generate_audio(), mimetype="audio/x-wav")

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
    print("app writing data set to false")

    response = {"message": "Data received successfully"}
    return jsonify(response)

@app.route("/start_call", methods=["POST"])
def start_call():
    app.writing_data = True
    chunk_handler.start_call()
    opener_text = "Hallo ich möchte gerne einen Termin für Florian Pfiel ausmachen. Haben Sie nächsten Donnerstag um neun uhr zeit?"
    conv_handler.append_initiator_text(opener_text)

    audio_segment = tts.text_to_speech_numpy_pmc(opener_text)
    # print(delta)
    bytes = audio_segment.tobytes()
    data_queue.put(get_wave_header())
    write_to_queue(bytes)

    response = {"message": "Alright alright alright!"}
    print("start call success")
    return jsonify(response)


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

    # print("reciving data")
    data = request.data

    data_with_head = get_wave_header(sample_rate=16000) + data
    data_np = np.frombuffer(data, dtype=np.int32)

    # print("chunk size", data_np.shape)
    data_processed, can_speak = chunk_handler.process_chunk(data_np)
    print("state: " + chunk_handler.state_machine.state)


    if chunk_handler.state_machine.state == "waiting_in_queue":
        print("waiting in queue")
        # chunk_handler.transition_to_wait() #TODO maybe remove in future
    elif chunk_handler.state_machine.state == "start_opener_speaking":
        
        #moved to /start_call for now ..
        # chunk_handler.transition_to_wait()
        print("from start_opener_speaking to wait")
    elif chunk_handler.state_machine.state == "start_speaking":
         
        last_answer = conv_handler.get_paragraph(role="receiver")

        gpt_answer =" "
        for delta in chatgpt.get_response_by_delimiter(last_answer):
            audio_segment = tts.text_to_speech_numpy_pmc(delta)
            gpt_answer += " " + delta
            bytes = audio_segment.tobytes()
            write_to_queue(bytes)
        
        # chunk_handler.transition_to_wait()
        conv_handler.append_initiator_text(gpt_answer)
        
    elif chunk_handler.state_machine.state == "speaking":
        print("still speaking")
        # n_chunks = data_np.shape[0] // 1000
        # write_to_queue(get_empty_wave_bytes(header=False, chunk_size=1000, n_chunks=n_chunks))
        # chunk_handler.transition_to_wait()


    elif chunk_handler.state_machine.state == "waiting":
        #listen to input
        print("waiting")
        transcript = voice_handler.handle_input_byte_string(data_with_head)
        if transcript is not None:
            conv_handler.append_receiver_text(transcript)
            print(transcript)
            n_chunks = data_np.shape[0] // 1000
            write_to_queue(get_empty_wave_bytes(header=False,n_chunks=n_chunks))

    
    # if chunk_handler.state_machine.state == "":

    response = jsonify("Alright alright alright!")
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

if __name__ == "__main__":
    app.run(host=os.environ.get("FLASK_HOST_IP", "localhost"))