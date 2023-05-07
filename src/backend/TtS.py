from nemo.collections.tts.models import FastPitchModel
from nemo.collections.tts.models import HifiGanModel
import numpy as np

import torch

class TextToSpeech():

    def __init__(self) -> None:
        self.spec_gen = FastPitchModel.restore_from("data/model_storage/tts_de_fastpitch_thorstens2210.nemo")
        self.spec_gen.eval()
        self.spec_gen.to("cuda")
    
        # model = HifiGanModel.from_pretrained(model_name="tts_de_hui_hifigan_ft_fastpitch_multispeaker_5")
        self.vocoder = HifiGanModel.restore_from("data/model_storage/tts_de_hifigan_thorstens2210.nemo")
        self.vocoder.eval()
        self.vocoder.to("cuda")

    def text_to_speech(self, text: str, pace = 0.8) -> torch.Tensor:
        speaker_id = 0
        with torch.no_grad():
            parsed = self.spec_gen.parse(text)
            spectrogram = self.spec_gen.generate_spectrogram(tokens=parsed, speaker=speaker_id, pace = pace)
            audio = self.vocoder.convert_spectrogram_to_audio(spec=spectrogram)
        return audio
    
    def text_to_speech_numpy_pmc(self, text: str, pace = 0.8) -> np.ndarray:
        audio_segment = self.text_to_speech(text, pace)
        audio_segment = torch.clamp(audio_segment, -1.0, 0.9999999)
        pcm_data = (audio_segment * 2147483647).to(torch.int32)

        return pcm_data.cpu().numpy()