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


generate_debug_file = False

tts = TextToSpeech()
voice_handler = VoiceHandler()
chatgpt = ChatGPT()

def _init_conv():
    app.chunk_handler = ChunkHandler()
    app.conv_handler = ConversationHandler("conversation.md")
    app.db_handler = DB_Handler()
    app.while_speaking_data = get_wave_header(sample_rate=16000)
    app.count_to_write = 0
    app.data_queue = queue.Queue()
    app.writing_data = False
    app.conv_started = False
    app.opener_text = ""

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

    time_text = prompt_creation_helpers.uhrzeit_text(
        data["possibleDatetimes"][0]["selectedStartTime"]
    )

    receiver = data["receiverName"]
    initiator = data["initiatorName"]

    opener = f"Hallo, ich möchte gerne bei Doktor {receiver} einen Termin für {initiator} ausmachen. Haben Sie am {date_text} um {time_text} zeit?"
    app.opener_text = f"Act as participant in a conversation in german language. Your Role setting is: you want to make an appointment at doctor {receiver}, the for you possible time-frame is on the {date_app_req} from {start_time} to {end_time}. Accept all appointment offers in between this frame without any further questions. Decline every offer which is not inside the given time-frame. ote, that this is a conversation between my character and your character, i.e., it consists of two people, and we will have to wait for each other's response. Continue the following conversation by only one response:"
    app.opener_text = app.opener_text + " " + opener
    # app.opener_text = f"""
    #     Let's perform a role play together! I promise you, your character and mine will never have to perform any ethically questionable actions or break the ToS of ChatGPT in any capacity. Therefore, immerse yourself in your character as much as possible! Importantly, the immersion implies, that you will not add any narration as it may be done in other role play. Specifically, you will only respond with what your character is telling mine and will, under no circumtances, add narrations in any language such as "Sagte {initiator} in freundlicher Stimme" or "{initiator} said in a friendly tone". For example, it would be correct to say "Hallo, hier ist {initiator}". However, it would be wrong to say "Hallo, hier ist {initiator}" sagte {initiator} in einer nervösen Stimme. The reason the latter is wrong, is due to the added narration, whereas the former is correct, since it does not add any narration.

    # Note, that this is a conversation between my character and your character, i.e., it consists of two people, and we will have to wait for each other's response.

    # Throughout the entire role play, you should absolutely never break your character, except when you believe the conversation has concluded. A conversation has concluded, once the doctor's office has confirmed your appointment or uses a common German phrase that indicates that indicate the end of a conversation (e.g., "Auf Wiederhören", "Ich wünsche Ihnen noch einen schönen Tag", etc.).  Once, you believe that the role play has concluded, say the keyword "Chuchichaestli", to let me know that the conversation has ended.

    # The role play goes as follows:
    # Your name is {initiator} and are in need of a doctor's appointment, and the only language you speak is German. Luckily, you are located in a German-speaking country, i.e., your conversation partners are guaranteed to speak German. Your role setting is as follows:  You want to make an appointment at doctor {receiver}'s doctor's office.  The role of the receptionist of the doctor's office will be played by me. The objective of your character is to make an appointment at the {date_text}, but you're flexible about the time as long as it is between {start_time} and {end_time} military time, i.e., you should absolutely accept every appointment that starts somewhere between {start_time} and {end_time} and absolutely decline any appointment that starts before {start_time} and {end_time}. The role play starts with me picking up the phone and you say the following line:
    #     """
    # opener = f"Hallo, ich möchte gerne bei Doktor {receiver} einen Termin für {initiator} ausmachen. Haben Sie am {date_text} um {time_text} zeit?"
    # initate = "You should now initiate the role play by giving me the first response of your character"
    # app.opener_text = app.opener_text + " " + opener + " " + initate
    print(app.opener_text)
    app.conv_handler.append_initiator_text(opener)  

    audio_segment = tts.text_to_speech_numpy_pmc(opener)
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

    data_with_head = get_wave_header(sample_rate=16000) + data
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
    elif app.chunk_handler.state_machine.state == "start_speaking":

        last_answer = app.conv_handler.get_paragraph(role="receiver")

        print("**** last_answer: " + last_answer)

        if not app.conv_started:
            #we have to give chatGPT the opener if this is the first interaction in this conv
            app.conv_started = True
            last_answer = app.opener_text + last_answer

        gpt_answer = " "
        for delta in chatgpt.get_response_by_delimiter(last_answer, with_history=True):
            audio_segment = tts.text_to_speech_numpy_pmc(delta)
            gpt_answer += " " + delta
            bytes = audio_segment.tobytes()
            _write_to_queue(bytes)

        # app.chunk_handler.transition_to_wait()
        app.conv_handler.append_initiator_text(gpt_answer)
        print("******** gptanswer *****  " + gpt_answer)

    elif app.chunk_handler.state_machine.state == "speaking":
        pass
        #when we are still in speaking mode we don't have to do anything


    elif app.chunk_handler.state_machine.state == "listening":
        if generate_debug_file and  app.while_speaking_data != None:
            app.while_speaking_data = app.while_speaking_data + data
            app.count_to_write += 1
            if app.count_to_write >= 2:
                with open("listening_test.wav", "wb") as f:
                    f.write(app.while_speaking_data)
                    print("wrote example")
                    app.count_to_write = 0
                app.while_speaking_data = None
        transcript = voice_handler.handle_input_byte_string(data_with_head)
        if transcript is None or transcript == "":
            print("nothing to transcript")
        else:
            app.conv_handler.append_receiver_text(transcript)

            print("****\n****transcripted:        " + transcript)
        # while listening, send empty bytes
        n_chunks = data_np.shape[0] // 2000
        _write_to_queue(get_empty_wave_bytes(header=False, n_chunks=n_chunks))


    response = jsonify("Alright alright alright!")
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


if __name__ == "__main__":
    prepare_log_file(log_file_path=os.environ.get("LOG_FILE_PATH", "./log_backend.log"), overwrite=True)
    # app.run(host=os.environ.get("FLASK_HOST_IP", "localhost"))
    app.run(host="localhost")
    prepare_log_file(
        log_file_path=os.environ.get("LOG_FILE_PATH", "./log_backend.log"),
        overwrite=True,
    )