# Load spectrogram generator
from nemo.collections.tts.models import FastPitchModel

spec_generator = FastPitchModel.restore_from(
    "data/model_storage/tts_de_fastpitch_thorstens2210.nemo"
)
spec_generator.eval()
spec_generator.to("cuda")

# Load Vocoder
from nemo.collections.tts.models import HifiGanModel

# model = HifiGanModel.from_pretrained(model_name="tts_de_hui_hifigan_ft_fastpitch_multispeaker_5")
model = HifiGanModel.restore_from(
    "data/model_storage/tts_de_hifigan_thorstens2210.nemo"
)
model.eval()
model.to("cuda")

import time

start_time = time.time()

# Generate audio
import torchaudio
to_parse = "Guten Tag!   Ich möchte gerne für Herrn Julian Harbort einen Termin ausmachen. Haben Sie nächste Woche Mittwoch um 9 Uhr noch einen Platz frei?"
# to_parse = """
# Es war ein gewöhnlicher Morgen, als ich den Hörer abnahm und die Praxis meines Arztes anrief. Ich musste einen Termin für meinen Freund Julian Harbort vereinbaren,
#  dessen Zustand eine dringende ärztliche Untersuchung erforderte."""
#  # Ein leichtes Beben erfasste mich, als ich die Stimme des Arztes hörte, dessen Autorität und Weisheit ich bewunderte.
#  # Ich fragte ihn, ob es möglich wäre, einen Termin für Julian am nächsten Mittwoch um 9 Uhr zu vereinbaren.
# #    """
# s = """
#      Ich gab dem Arzt den Namen meines Freundes und seine Kontaktdaten, falls weitere Informationen benötigt würden. Der Arzt beruhigte mich und sagte, dass er alles im Griff hätte.'Vielen Dank', sagte ich erleichtert. 
#      'Wir werden uns auf den Termin vorbereiten und sehen uns nächste Woche.''Sehr gerne', antwortete der Arzt. 'Bis bald.'Ich legte den Hörer auf und seufzte. Es war ein kleiner Sieg, aber ein Sieg dennoch. 
#      Ich wusste, dass Julian in guten Händen sein würde und dass der Arzt alles tun würde, um ihm zu helfen. Es war ein Moment der Erleichterung, aber auch ein Moment der Dankbarkeit.
#      """
parsed = spec_generator.parse(to_parse)
speaker_id = 0
with torch.no_grad():
    spectrogram = spec_generator.generate_spectrogram(tokens=parsed, speaker=speaker_id, pace = 0.7)
    audio = model.convert_spectrogram_to_audio(spec=spectrogram)

# Save the audio to disk in a file called speech.wav
torchaudio.save('german_speech3.wav', audio.cpu(), 22050)   

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Elapsed time: {elapsed_time:.5f} seconds")

import sounddevice as sd

# Define a callback function that will be called for each block of audio data
def callback(indata, frames, time, status):
    if status:
        print(status)
    outstream.write(indata.copy())

# Set up the sound stream
blocksize = 1024
samplerate = 22050
channels = 1
dtype = 'float32'

outstream = sd.OutputStream(blocksize=blocksize, samplerate=samplerate, channels=channels, dtype=dtype, callback=callback)
outstream.start()

# Wait for the audio to finish playing
while outstream.active:
    pass
