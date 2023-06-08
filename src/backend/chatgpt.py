import os
from typing import Generator, Tuple

import openai

class ChatGPT:
    def __init__(self, user_delimiter = "#u#", assistant_delimiter = "#a#") -> None:
        self.user_delimiter = user_delimiter
        self.assistant_delimiter = assistant_delimiter
        self.messages = []
        openai.api_key = os.environ["OPENAI_API_KEY"]

    def add_system_message(self, message: str) -> None:
        self.messages.append({"role": "system", "content": message})

    def add_assistant_message(self, message: str) -> None:
        self.messages.append({"role": "assistant", "content": f"{self.assistant_delimiter}{message}{self.assistant_delimiter}"})
    
    def add_user_message(self, message: str) -> None:
        self.messages.append({"role": "user", "content": f"{self.user_delimiter}{message}{self.user_delimiter}"})

    def get_response(self, message: str) -> Generator[Tuple[str, str], None, None]:
        msgs = [{"role": "user", "content": f"{self.user_delimiter}{message}{self.user_delimiter}"}]
       
        completions = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=msgs,
            stream=True,
            temperature=0.2
        )

        result_str = ""

        for completion in completions:
            response = completion["choices"][0]["delta"]

            if "content" in response.keys():
                delta = response["content"]
                result_str += delta.replace(self.assistant_delimiter, "")
                yield (delta, result_str)

    def get_response_with_history(self, message: str) -> Generator[Tuple[str, str], None, None]:
        
        self.add_user_message(message)
 
        completions = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages,
            stream=True,
        )

        result_str = ""

        for completion in completions:
            response = completion["choices"][0]["delta"]

            if "content" in response.keys():
                delta = response["content"]
                result_str += " " + delta.replace(self.assistant_delimiter, "")
                yield (delta, result_str)

        self.add_assistant_message(result_str)

    def get_response_by_delimiter(self, message: str, with_history : bool = False, delimiter=[",", ".", "!", "?",":"]):
        buffer = ""
        gen = self.get_response_with_history(message) if with_history else self.get_response(message)
        for delta, result in gen:
            buffer += delta
            if delta in delimiter:
                yield buffer
                buffer = ""
        if buffer != "":
            yield buffer
