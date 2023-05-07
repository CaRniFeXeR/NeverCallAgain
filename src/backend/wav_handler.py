import struct

def get_wave_header(num_channels = 1, bits_per_sample = 32, sample_rate = 22050, len_bytes = 0):

    # sample_rate = 22050  # example sample rate
    # num_channels = 1  # example number of channels
    # bits_per_sample = 32  # example bit depth

    # len_bytes = 0 #len(audio_bytes)

    # Calculate the total number of audio frames based on the length of your byte array
    num_frames = len_bytes // (num_channels * bits_per_sample // 8)

    # Construct the WAV header as a byte array
    wav_header = struct.pack('<4sI4s4sIHHIIHH4sI',
                            b'RIFF',
                            36 + len_bytes,
                            b'WAVE',
                            b'fmt ',
                            16,
                            1,  # PCM audio format
                            num_channels,
                            sample_rate,
                            sample_rate * num_channels * bits_per_sample // 8,
                            num_channels * bits_per_sample // 8,
                            bits_per_sample,
                            b'data',
                            len_bytes)
    
    return wav_header