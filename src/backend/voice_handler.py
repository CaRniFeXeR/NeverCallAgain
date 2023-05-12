from typing import IO

import numpy as np

from .StT import SpeechToText


class VoiceHandler:
    """
    VoiceHandler is a class that handles all voice related operations.
    """

    def __init__(self, chunk_size=1024) -> None:
        self.stt = SpeechToText()
        self.chunk_size = chunk_size

    def handle_input_stream(self, stream: IO[bytes]):
        """
        Handles an input stream of bytes.
        """
        transcript = self.stt.speech_to_text(np.array(stream.read(self.chunk_size)))

        print(transcript)
