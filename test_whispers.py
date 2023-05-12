import torch
from datasets import load_dataset
from transformers import pipeline

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# Load pipeline
pipe = pipeline(
    "automatic-speech-recognition",
    model="bofenghuang/whisper-large-v2-cv11-german",
    device=device,
)

# NB: set forced_decoder_ids for generation utils
pipe.model.config.forced_decoder_ids = pipe.tokenizer.get_decoder_prompt_ids(
    language="de", task="transcribe"
)

# Load data
ds_mcv_test = load_dataset(
    "mozilla-foundation/common_voice_11_0", "de", split="test", streaming=True
)
test_segment = next(iter(ds_mcv_test))
waveform = test_segment["audio"]

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

# Run
generated_sentences = pipe(waveform)["text"]

print(generated_sentences)
