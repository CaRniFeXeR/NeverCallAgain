# open .wav file
# fill content of wave file to chunk handler to process chunk
import numpy as np


def open_wav_file(path: str) -> np.ndarray:
    # preferableb bitestring but numpy array is okay 32 bit signed integer
    with open(path, "rb") as wav_bytes:
        wav_data = np.frombuffer(wav_bytes.read(), dtype=np.int32)
        return wav_data

