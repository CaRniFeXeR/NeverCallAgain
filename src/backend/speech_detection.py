"""
    Naive: Learn wake words, we need to stage our demo that this isn't visible

    Less naive: Filter out music and noise, or map it to a static pattern e.g., "00000000", and configure
     --> "Problem" does nemo already filter out music and noise? If so, we can just use the output of the TtS module

    chunks of audio as numpy arrays (1 channel) (1024 amplitude samples) 32-bit signed integers
"""
import time

import numpy as np
import nemo
import os
import nemo.collections.asr as nemo_asr
import pvcobra as pvcobra
import struct

import pyaudio


class SpeechDetection:
    def __init__(self, model_name: str = "QuartzNet15x5Base-En") -> None:
        self.command_recognition = nemo_asr.models.ASRModel.from_pretrained(model_name=model_name)
        pv_access_key = os.environ.get("PICOVOICE_API_KEY")
        assert pv_access_key, "PICOVOICE_API_KEY environment variable not set"
        self.cobra = pvcobra.create(access_key=pv_access_key)

    def silence_detection(self, audio_chunk: np.ndarray) -> bool:
        if self.cobra.process(audio_chunk) > 0.2:
            return True
        return False

    def music_detection(self) -> bool:
        pass
