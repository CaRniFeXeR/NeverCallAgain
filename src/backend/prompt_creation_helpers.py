def datum_text(datum: str) -> str:
    monate = {
        "01": "Januar",
        "02": "Februar",
        "03": "März",
        "04": "April",
        "05": "Mai",
        "06": "Juni",
        "07": "Juli",
        "08": "August",
        "09": "September",
        "10": "Oktober",
        "11": "November",
        "12": "Dezember",
    }

    day_dict = {
        1: "ersten",
        2: "zweiten",
        3: "dritten",
        4: "vierten",
        5: "fünften",
        6: "sechsten",
        7: "siebten",
        8: "achten",
        9: "neunten",
        10: "zehnten",
        11: "elften",
        12: "zwölften",
        13: "dreizehnten",
        14: "vierzehnten",
        15: "fünfzehnten",
        16: "sechzehnten",
        17: "siebzehnten",
        18: "achtzehnten",
        19: "neunzehnten",
        20: "zwanzigsten",
        21: "einundzwanzigsten",
        22: "zweiundzwanzigsten",
        23: "dreiundzwanzigsten",
        24: "vierundzwanzigsten",
        25: "fünfundzwanzigsten",
        26: "sechsundzwanzigsten",
        27: "siebenundzwanzigsten",
        28: "achtundzwanzigsten",
        29: "neunundzwanzigsten",
        30: "dreißigsten",
        31: "einunddreißigsten",
    }

    _, monat, tag = datum.split("-")
    tag = int(tag)
    monat = monate[monat]

    tag_text = day_dict[tag]

    return "{} {}".format(tag_text, monat)


def uhrzeit_text(time_str):
    # Dictionary für Minuten
    minute_dict = {
        0: "",
        1: "eins",
        2: "zwei",
        3: "drei",
        4: "vier",
        5: "fünf",
        6: "sechs",
        7: "sieben",
        8: "acht",
        9: "neun",
        10: "zehn",
        11: "elf",
        12: "zwölf",
        13: "dreizehn",
        14: "vierzehn",
        15: "fünfzehn",
        16: "sechzehn",
        17: "siebzehn",
        18: "achtzehn",
        19: "neunzehn",
        20: "zwanzig",
        21: "einundzwanzig",
        22: "zweiundzwanzig",
        23: "dreiundzwanzig",
        24: "vierundzwanzig",
        25: "fünfundzwanzig",
        26: "sechsundzwanzig",
        27: "siebenundzwanzig",
        28: "achtundzwanzig",
        29: "neunundzwanzig",
        30: "dreißig",
        31: "einunddreißig",
        32: "zweiunddreißig",
        33: "dreiunddreißig",
        34: "vierunddreißig",
        35: "fünfunddreißig",
        36: "sechsunddreißig",
        37: "siebenunddreißig",
        38: "achtunddreißig",
        39: "neununddreißig",
        40: "vierzig",
        41: "einundvierzig",
        42: "zweiundvierzig",
        43: "dreiundvierzig",
        44: "vierundvierzig",
        45: "fünfundvierzig",
        46: "sechsundvierzig",
        47: "siebenundvierzig",
        48: "achtundvierzig",
        49: "neunundvierzig",
        50: "fünfzig",
        51: "einundfünfzig",
        52: "zweiundfünfzig",
        53: "dreiundfünfzig",
        54: "vierundfünfzig",
        55: "fünfundfünfzig",
        56: "sechsundfünfzig",
        57: "siebenundfünfzig",
        58: "achtundfünfzig",
        59: "neunundfünfzig",
        60: "sechzig",
    }

    hour_dict = {
        0: "null",
        1: "eins",
        2: "zwei",
        3: "drei",
        4: "vier",
        5: "fünf",
        6: "sechs",
        7: "sieben",
        8: "acht",
        9: "neun",
        10: "zehn",
        11: "elf",
        12: "zwölf",
        13: "dreizehn",
        14: "vierzehn",
        15: "fünfzehn",
        16: "sechzehn",
        17: "siebzehn",
        18: "achtzehn",
        19: "neunzehn",
        20: "zwanzig",
        21: "einundzwanzig",
        22: "zweiundzwanzig",
        23: "dreiundzwanzig",
    }

    # Split the input string at the colon
    hour, minute = time_str.split(":")

    # Convert the hour to integer
    hour = int(hour)

    # Convert the minute to integer
    minute = int(minute)

    hour_text = hour_dict[hour]
    minute_text = minute_dict[minute]

    # Build the final text
    if minute == 0:
        final_text = hour_text + " Uhr"
    else:
        final_text = hour_text + " Uhr " + minute_text

    return final_text


def date_to_string(date_str):
    # Mapping von Monatsnummern zu Monatsnamen
    months = {
        "01": "Januar",
        "02": "Februar",
        "03": "März",
        "04": "April",
        "05": "Mai",
        "06": "Juni",
        "07": "Juli",
        "08": "August",
        "09": "September",
        "10": "Oktober",
        "11": "November",
        "12": "Dezember",
    }

    _, month, day = date_str.split("-")

    month_str = months[month]

    return f"{day}.{month_str}"
