import time
import torch

# from datasets import load_dataset
from transformers import pipeline

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# Load pipeline
#big, small etc
pipe = pipeline("automatic-speech-recognition", model="bofenghuang/whisper-small-cv11-german", device=device)

# NB: set forced_decoder_ids for generation utils
pipe.model.config.forced_decoder_ids = pipe.tokenizer.get_decoder_prompt_ids(language="de", task="transcribe")
pipe.model.eval()

# NB: decoding option
# limit the maximum number of generated tokens to 225
pipe.model.config.max_length = 225 + 1
# sampling
# pipe.model.config.do_sample = True
# beam search
# pipe.model.config.num_beams = 5
# return
# pipe.model.config.return_dict_in_generate = True
# pipe.model.config.output_scores = True
# pipe.model.config.num_return_sequences = 5

start_time = time.time()

import soundfile as sf
# load wave file from disk
waveform, sr = sf.read("out.wav")

# Run
with torch.no_grad():
    generated_sentences = pipe(waveform)["text"]

print(generated_sentences)

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Elapsed time: {elapsed_time:.5f} seconds")
