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

    date_text = prompt_creation_helpers.datum_text(
        data["possibleDatetimes"][0]["selectedDate"]
    )

    time_text = prompt_creation_helpers.uhrzeit_text(
        data["possibleDatetimes"][0]["selectedStartTime"]
    )

    receiver = data["receiverName"]
    initiator = data["initiatorName"]

    opener_text = f"Hallo, ich möchte gerne bei Doktor { receiver } einen Termin für {initiator} ausmachen. Haben Sie am {date_text} um {time_text} zeit?"

    print(opener_text)

    status_code = 200
    return opener_text, status_code


if __name__ == "__main__":
    app.run(debug=True)
