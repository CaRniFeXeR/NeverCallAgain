import os
import time
from typing import Generator, Tuple

import openai

# print(openai.Model.list())


def test(text):
    text = text.replace("\n", " ")


class ChatGPT:
    pass

    def __init__(self) -> None:
        openai.api_key = os.environ["OPENAI_API_KEY"]

    def get_response(self, message: str) -> Generator[Tuple[str, str], None, None]:

        completions = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}],
            stream=True,
        )

        result_str = ""

        for completion in completions:
            response = completion["choices"][0]["delta"]
            if "content" in response.keys():
                delta = response["content"]
                result_str += " " + delta
                yield (delta, result_str)

    def get_response_by_delimiter(self, message: str, delimiter=[",", ".", "!"]):
        buffer = ""
        for delta, result in self.get_response(message):
            buffer += delta
            if delta in delimiter:
                yield buffer
                buffer = ""
        if buffer != "":
            yield buffer
