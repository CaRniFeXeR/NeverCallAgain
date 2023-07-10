# NeverCallAgain

Automated Doctor's Appointment Calls in German based on three Deep Learning models.


## Techstack

We use two open-source models for Speech to Text (STT) and Text to Speech (TTS) translation as well as ChatGPT for dialog generation. 

- **STT**: Whisper-Medium fine-tuned for ASR in German from [Hugging Face](https://huggingface.co/bofenghuang/whisper-medium-cv11-german)
- **TTS**: [Nvidia NEMO FastPitch HiFi-GAN](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/nemo/models/tts_de_fastpitchhifigan) trained on german speech
- **LLM** : ChatGPT API gpt-3.5-turbo
- **FrontEnd**: vue.js
- **Backend**: Python Flask
- **audio streaming**: via webinterface with [audioWorklet](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet)


## Demo

run [flask_api.py](/src/backend/flask_api.py) to serve the application under http://localhost. 

Microphone and speaker access is needed as all audio data is stream via the webinterface.

You can also host the web server on one machine and access the web interface from another machine (e.g. smartphone).

![demo](/assets/call_management_demo.png)

## Approach

![overview](/assets/approach_overview.jpg)


