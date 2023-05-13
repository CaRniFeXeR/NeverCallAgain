from src.backend.chunk_handler import ChunkHandler
from src.backend.tests.test_util import open_wav_file


# with pytests we could work with fixtures and stuff, but for now we just test the functions with hardcoded resources


def can_detect_silence() -> None:
    chunk_handler = ChunkHandler()
    chunk_handler.state_machine.state = "waiting"
    # sec 3-6 silence~
    wav_np_array = open_wav_file("src/backend/tests/test_data/wav_files/recording_test_silence.wav")
    chunk_size = 22000  # hard code this for now (should have 3 seconds of silence)
    chunks = wav_np_array.shape[0] // chunk_size
    for i in range(0, chunks):
        ch = wav_np_array[i * chunk_size: (i + 1) * chunk_size]
        chunk_handler.process_chunk(ch)


can_detect_silence()
