import json
import os
import queue
import time
import prompt_creation_helpers
import flask
import numpy as np
from chunk_handler import ChunkHandler
from conversation_handler import ConversationHandler
from chatgpt import ChatGPT
from flask import Flask, Response, jsonify, request, send_from_directory
from TtS import TextToSpeech
from src.backend.logging_util import def_logger, prepare_log_file
from voice_handler import VoiceHandler
from wav_handler import get_empty_wave_bytes, get_wave_header, split_wave_bytes_into_chunks
from db_handler import DB_Handler
from call_model import Call
logger = def_logger.getChild(__name__)


app = Flask(__name__, static_folder="./../frontend")


generate_debug_file = True

tts = TextToSpeech()
voice_handler = VoiceHandler()
chatgpt = ChatGPT()

def _init_conv():
    app.chunk_handler = ChunkHandler()
    app.conv_handler = ConversationHandler("conversation.md")
    app.db_handler = DB_Handler()
    app.listening_audio = b""
    app.count_to_write = 0
    app.data_queue = queue.Queue()
    app.writing_data = False
    app.conv_started = False
    app.opener_text = ""

def _get_listening_audio() -> bytes:
    return get_wave_header(1, 32, 16000, len(app.listening_audio)) + app.listening_audio

_init_conv()

def _write_to_queue(bytes):
    # print("write_to_queue")
    for byte_chunk in split_wave_bytes_into_chunks(bytes):
        app.data_queue.put(byte_chunk)


def _generate_audio():
    print("generate_audio")
    # stream_count = 0
    if not app.writing_data and app.data_queue.empty():
        time.sleep(1) 
    while app.writing_data or not app.data_queue.empty():
        if not app.data_queue.empty():
            data = app.data_queue.get()
            yield data
            # stream_count += 1
            # print(f"streaming audio back {stream_count}")
        if app.writing_data and app.data_queue.empty():
            time.sleep(0.5)
            print("waiting for new audio data to stream...")

    print("finished gen audio")


@app.route("/reset_conv", methods=["POST"])
def reset_conv():
    _init_conv()

    response = {"message": "Reset performed successfully"}
    return jsonify(response)

@app.route("/stream_audio")
def stream_audio():
    return Response(_generate_audio(), mimetype="audio/x-wav")

@app.route("/calls", methods=["GET"])
def get_calls():
    calls = app.db_handler.getAllCalls()
    return [json.dumps(call.__dict__) for call in calls]

@app.route("/add_call", methods=["POST"])
def add_call():
    print(request.headers)
    call_json = request.get_json()
    new_call = Call(**call_json)
    app.db_handler.insertNewCall(new_call)
    return "Call erfolgreich erstellt", 201


@app.route("/start_call", methods=["POST"])
def start_call():
    app.writing_data = True
    app.conv_started = False
    app.chunk_handler.start_call()
    data = request.json
    # data = {'title': 'asdadasd', 'state': 1, 'receiverName': 'Deim', 'receiverPhonenr': 'dfdf', 'initiatorName': 'Hoffmann', 'possibleDatetimes': [{'selectedDate': '2023-05-20', 'selectedStartTime': '08:00', 'selectedEndTime': '12:00'}], 'result': None}
    new_call = Call(**data)
    app.db_handler.insertNewCall(new_call)
    date_app_req = prompt_creation_helpers.date_to_string(
        data["possibleDatetimes"][0]["selectedDate"]
    )
    start_time = data["possibleDatetimes"][0]["selectedStartTime"]
    end_time = data["possibleDatetimes"][0]["selectedEndTime"]

    date_text = prompt_creation_helpers.datum_text(
        data["possibleDatetimes"][0]["selectedDate"]
    )

    start_time_text = prompt_creation_helpers.uhrzeit_text(start_time)

    end_time_text = prompt_creation_helpers.uhrzeit_text(end_time)

    receiver = data["receiverName"]
    initiator = data["initiatorName"]

    opener_text = f"Hallo, ich möchte gerne bei Doktor {receiver} einen Termin für {initiator} ausmachen. Haben Sie am {date_text} um {start_time_text} zeit?"
    system_instruction = f"""
        Act as participant in a conversation in german language between you and appointment manager.
        The appointment managers responses will be delimited with {chatgpt.user_delimiter} characters. 
        Any previous reponses of you are delimited with {chatgpt.assistant_delimiter} characters.
        Your Role setting is: you want to make an appointment at doctor {receiver},
        the for you possible time-frame is on the {date_app_req} from {start_time_text} to {end_time_text}. 
        Accept all appointment offers in between this time-frame without any further questions. 
        For instance, if your possible time-frame is from 2pm to 4pm, accept an offer at 2:30pm or any offer between 2pm and 4pm.
        Decline every offer which is not within the given time-frame. Don't forget that time in german is written in the 24h format.
        Continue the following conversation by one response of you, the caller. Do not write any repsonse of the appointment manager."""
   
    print(system_instruction)
    app.conv_handler.append_initiator_text(opener_text)  
    chatgpt.add_system_message(system_instruction)
    chatgpt.add_assistant_message(opener_text)

    audio_segment = tts.text_to_speech_numpy_pmc(opener_text)
    # print(delta)
    bytes = audio_segment.tobytes()
    app.data_queue.put(get_wave_header())
    _write_to_queue(bytes)

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

    data = request.data

    # data_with_head = get_wave_header(sample_rate=16000, len_bytes=len(data)) + data
    data_np = np.frombuffer(data, dtype=np.int32)

    # print("chunk size", data_np.shape)
    data_processed, can_speak = app.chunk_handler.process_chunk(data_np)
    print("state: " + app.chunk_handler.state_machine.state)

    if app.chunk_handler.state_machine.state == "waiting_in_queue":
        pass
        # print("waiting in queue")
        # app.chunk_handler.transition_to_wait() #TODO maybe remove in future
    elif app.chunk_handler.state_machine.state == "start_opener_speaking":

        # moved to /start_call for now ..
        # app.chunk_handler.transition_to_wait()
        # print("from start_opener_speaking to wait")
        pass

    elif app.chunk_handler.state_machine.state == "listening":
        # we detected speech and now are listening to the other person
        app.listening_audio = app.listening_audio + data

        if generate_debug_file and app.count_to_write != -1:
            app.count_to_write += 1
            if app.count_to_write >= 3:
                with open("listening_test.wav", "wb") as f:
                    f.write(_get_listening_audio())
                    print("wrote example")
                    app.count_to_write = -1
  
        # while listening, send empty bytes
        n_chunks = data_np.shape[0] // 2000
        _write_to_queue(get_empty_wave_bytes(header=False, n_chunks=n_chunks))
    elif app.chunk_handler.state_machine.state == "start_speaking":


        transcript = voice_handler.handle_input_byte_string(_get_listening_audio())
        app.listening_audio = b""
        if transcript is None or transcript == "":
            print("nothing to transcript")
        else:
            app.conv_handler.append_receiver_text(transcript)

            print("****\n****transcripted:        " + transcript)

            print("**** user_answer: " + transcript)
            gpt_answer = " "
            for delta in chatgpt.get_response_by_delimiter(transcript, with_history=True):
                res_delta = delta.replace(" a ", "").replace("#a #","").replace(chatgpt.assistant_delimiter, "").replace("#","")
                audio_segment = tts.text_to_speech_numpy_pmc(res_delta)
                gpt_answer += " " + res_delta
                bytes = audio_segment.tobytes()
                _write_to_queue(bytes)

            # app.chunk_handler.transition_to_wait()
            app.conv_handler.append_initiator_text(gpt_answer)
            print("******** assistance answer *****  " + gpt_answer)

    elif app.chunk_handler.state_machine.state == "speaking":
        pass
        #when we are still in speaking mode we don't have to do anything



    response = jsonify("Alright alright alright!")
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


if __name__ == "__main__":
    prepare_log_file(log_file_path=os.environ.get("LOG_FILE_PATH", "./log_backend.log"), overwrite=True)
    # app.run(host=os.environ.get("FLASK_HOST_IP", "localhost"))
    app.run(host='0.0.0.0', port=5000)
    prepare_log_file(
        log_file_path=os.environ.get("LOG_FILE_PATH", "./log_backend.log"),
        overwrite=True,
    )