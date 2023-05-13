from typing import Dict, List, Tuple


class ConversationHandler:
    def __init__(self):
        self._initiator_text: Dict[int, List[str]] = dict()
        self._receiver_text: Dict[int, List[str]] = dict()
        self._stepper: int = 0
        self.control = None

    def append_initiator_text(self, text: str) -> None:
        if self.control != "A":
            self._stepper += 1
            self.control = "A"
        paragraph = self._initiator_text.get(self._stepper)
        if paragraph:
            paragraph.append(text)
            self._initiator_text[self._stepper] = paragraph
        else:
            paragraph = [text]
            self._initiator_text[self._stepper] = paragraph

    def append_receiver_text(self, text: str) -> None:
        if self.control != "B":
            self._stepper += 1
            self.control = "B"

        paragraph = self._receiver_text.get(self._stepper)
        if paragraph:
            paragraph.append(text)
            self._receiver_text[self._stepper] = paragraph
        else:
            paragraph = [text]
            self._receiver_text[self._stepper] = paragraph

    def clear(self) -> None:
        self._initiator_text = dict()
        self._receiver_text = dict()
        self._stepper = 0

    def get_paragraph(self, role: str = "receiver", paragraph: int = -1, paragraph_sep: str = "\n"):
        """
            Returns the paragraph of the conversation.

            By default, the last paragraph is returned.
        """
        if role == "initiator":
            text_list = self._initiator_text[paragraph]
        elif role == "receiver":
            text_list = self._receiver_text[paragraph]
        else:
            raise ValueError("Invalid role")

        return paragraph_sep.join(text_list)

    def build_conversation(self, role_prefixes: Tuple[str, str] = ("A: ", "B: "), paragraph_sep: str = "\n") -> str:
        def _build_graphraph(paragraph_list: List[str], role_prefix: str) -> str:
            return role_prefix + paragraph_sep.join(paragraph_list) + "\n"

        merged_text = ''
        initator_prefix, receiver_prefix = role_prefixes
        for key in sorted(list(set(self._initiator_text.keys()).union(self._receiver_text.keys()))):
            if key in self._initiator_text:
                paragraph = paragraph_sep.join(self._initiator_text[key])
                prefix = initator_prefix
            elif key in self._receiver_text:
                paragraph = paragraph_sep.join(self._receiver_text[key])
                prefix = receiver_prefix
            else:
                raise ValueError("Invalid key")
            merged_text += _build_graphraph(paragraph, prefix)
