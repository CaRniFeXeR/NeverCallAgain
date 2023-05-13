from flask import Flask
from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS
import re
import prompt_creation_helpers


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/")
@app.route("/home")
def home():
    return "Welcome to the home page"


@app.route("/data_management")
def data_management():
    return "Data management page"


@app.route("/start_call", methods=["POST"])
def start_call():
    data = request.json
    print(data)

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

    app.opener_text = f"Act as participant in a conversation in german language. Your Role setting is: you want to make an appointment at doctor meier, the for you possible time-frame is on the {date_app_req} from {start_time} to {end_time}. Accept all appointment offers in between this frame without any further questions. Decline every offer which is not inside the given time-frame. Continue the following conversation by only one response:"
    +f"Hallo, ich möchte gerne bei Doktor { receiver } einen Termin für {initiator} ausmachen. Haben Sie am {date_text} um {time_text} zeit?"

    status_code = 200
    return status_code


if __name__ == "__main__":
    app.run(debug=True)
