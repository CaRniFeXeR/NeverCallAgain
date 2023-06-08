import numpy as np
import torch
from transformers import pipeline

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


class SpeechToText:
    def __init__(self, fs=16000) -> None:
        self.fs = fs
        # either use whisper small or medium
        self.model_pipe = pipeline(
            "automatic-speech-recognition",
            model="bofenghuang/whisper-medium-cv11-german",
            device=device
            # max_new_tokens=300
        )
        self.model_pipe.model.config.forced_decoder_ids = self.model_pipe.tokenizer.get_decoder_prompt_ids(
            language="de", task="transcribe")
        self.model_pipe.model.eval()

    def speech_to_text(self, audio: np.ndarray):
        with torch.no_grad():
            generated_sentences = self.model_pipe(audio)["text"]

        return generated_sentences
