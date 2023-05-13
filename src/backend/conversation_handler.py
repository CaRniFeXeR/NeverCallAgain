from typing import List


class ConversationHandler:
    def __init__(self):
        self._initiator_text: List[str] = []
        self._receiver_text = List[str] = []

    def append_initiator_text(self, text: str):
        self._initiator_text.append(text)

    def append_receiver_text(self, text: str):
        self._receiver_text.append(text)

    def clear(self):
        self._initiator_text = []
        self._receiver_text = []
