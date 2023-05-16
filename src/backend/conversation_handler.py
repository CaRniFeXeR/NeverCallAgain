import logging
from pathlib import Path
from typing import Dict, List, Tuple

from logging_util import def_logger

logger = def_logger.getChild(__name__)


class ConversationHandler:
    def __init__(self, output_location : Path = None):
        self._initiator_text: Dict[int, List[str]] = dict()
        self._receiver_text: Dict[int, List[str]] = dict()
        self._stepper: int = 0
        self.control = None
        self.output_location = output_location

    def append_initiator_text(self, text: str) -> None:
        if self.control != "A":
            self._stepper += 1
            self.control = "A"

        self._append_text(self._initiator_text, text)

    def append_receiver_text(self, text: str) -> None:
        if self.control != "B":
            self._stepper += 1
            self.control = "B"

        self._append_text(self._receiver_text, text)

    def _append_text(self, dict : Dict[int, List[str]], text: str) -> None:
        paragraph = dict.get(self._stepper)
        if paragraph:
            paragraph.append(text)
            dict[self._stepper] = paragraph
        else:
            paragraph = [text]
            dict[self._stepper] = paragraph

        if self.output_location != None:
            self.save_conversation(self.output_location)

        

    def clear(self) -> None:
        self._initiator_text = dict()
        self._receiver_text = dict()
        self._stepper = 0

    def get_paragraph(
        self, role: str = "receiver", paragraph: int = -1, paragraph_sep: str = " "
    ):
        """
        Returns the paragraph of the conversation.

        By default, the last paragraph is returned.
        """
        if role == "initiator":
            text_list = self._initiator_text[
                paragraph if paragraph != -1 else max(self._initiator_text.keys())
            ]
        elif role == "receiver":
            text_list = self._receiver_text[
                paragraph if paragraph != -1 else max(self._receiver_text.keys())
            ]
        else:
            raise ValueError("Invalid role")

        paragraph_text = paragraph_sep.join(text_list)
        logger.debug(f"Returning paragraph: {paragraph_text}")
        return paragraph_text

    def build_conversation(
        self, role_prefixes: Tuple[str, str] = ("### Bot: \n", "### Human: \n"), paragraph_sep: str = " "
    ) -> str:

        merged_text = ""
        initator_prefix, receiver_prefix = role_prefixes
        for key in sorted(
            list(set(self._initiator_text.keys()).union(self._receiver_text.keys()))
        ):
            if key in self._initiator_text:
                paragraph = paragraph_sep.join(self._initiator_text[key])
                prefix = initator_prefix
            elif key in self._receiver_text:
                paragraph = paragraph_sep.join(self._receiver_text[key])
                prefix = receiver_prefix
            else:
                raise ValueError("Invalid key")
            merged_text += f"{prefix}{paragraph}\n"

        return merged_text

    def save_conversation(self, path: str) -> None:
        #save as txt file
        with open(path, "w") as f:
            f.write(self.build_conversation())
