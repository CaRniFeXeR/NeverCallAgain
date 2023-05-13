

from src.backend.voice_handler import VoiceHandler


#load wav file "test.wav " as byte string
with open("listening_test.wav", "rb") as f:
    byte_string = f.read()

vh = VoiceHandler()
transcribe = vh.handle_input_byte_string(byte_string)

print(transcribe)