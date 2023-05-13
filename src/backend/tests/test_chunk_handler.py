from src.backend.chunk_handler import ChunkHandler
from src.backend.tests.test_util import open_wav_file


# with pytests we could work with fixtures and stuff, but for now we just test the functions with hardcoded resources


def can_detect_silence() -> None:
    chunk_handler = ChunkHandler()
    chunk_handler.state_machine.state = "speaking"
    # sec 3-6 silence~
    wav_np_array = open_wav_file("src/backend/tests/test_data/wav_files/baseline_noise_silence.wav")
    # wav_np_array = open_wav_file("src/backend/tests/test_data/wav_files/baseline_speaking.wav")
    # wav_np_array = open_wav_file("src/backend/tests/test_data/wav_files/julian.wav")
    chunk_size = 2000  # hard code this for now (should have 3 seconds of silence)
    chunks = wav_np_array.shape[0] // chunk_size
    for i in range(0, chunks):
        ch = wav_np_array[i * chunk_size: (i + 1) * chunk_size]
        chunk_handler.process_chunk(ch)

""""
0.005761423623543896
0.009259490910107034
0.010294278845095206
0.01611015207279015
0.012758294069095651
0.007454632244750221
0.008152222823189675
0.003859876866387146
0.010389445667103606
0.0062704508997362355
0.004367171652320387
0.025091293781572623
0.026320972528923757
0.005442400183036178
0.008887603629560955
"""
can_detect_silence()
