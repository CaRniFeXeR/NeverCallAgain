# Load spectrogram generator
from nemo.collections.tts.models import FastPitchModel
spec_generator = FastPitchModel.restore_from("path/to/model.nemo")

# Load Vocoder
from nemo.collections.tts.models import HifiGanModel
model = HifiGanModel.from_pretrained(model_name="tts_de_hui_hifigan_ft_fastpitch_multispeaker_5")

# Generate audio
import torchaudio
parsed = spec_generator.parse("")
speaker_id = 0
spectrogram = spec_generator.generate_spectrogram(tokens=parsed, speaker=speaker_id)
audio = model.convert_spectrogram_to_audio(spec=spectrogram)

# Save the audio to disk in a file called speech.wav
torchaudio.save('german_speech.wav', audio.cpu(), 44100)
import pynini