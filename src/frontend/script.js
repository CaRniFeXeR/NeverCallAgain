const form = document.getElementById("myForm");
form.addEventListener("submit", function (event) {
  event.preventDefault(); // prevent the default form submission behavior

  const input = document.getElementById("text_input");
  const inputValue = input.value;

  const data = { text_input: inputValue };
  const options = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  };

  fetch("/submit", options)
    .then((response) => response.json())
    .then((data) => console.log(data))
    .catch((error) => console.error(error));
});

// onclick button with id audio_click

const btn = document.getElementById("audio_btn");

function registerAudioPlayBackStream() {
  var div = document.getElementById("audio_container")

  div.innerHTML = `
    <audio controls="">
    <source id="audio_src" type="audio/x-wav" sampleRate=22050 src="/stream_audio">
    </audio>  
  `

  const audio = document.getElementById("audio_src");

  // Wait until the audio is loaded and ready to play
  audio.addEventListener("canplay", function() {
    audio.play();
  });
}

btn.onclick = function () {
  registerAudioPlayBackStream()
}

const micro_btn = document.getElementById("micro_btn");

function handleMicStream(streamObj) {
  // keep the context in a global variable
  stream = streamObj;

  input = audioContext.createMediaStreamSource(stream);

  input.connect(processor);

  processor.onaudioprocess = (e) => {
    microphoneProcess(e); // receives data from microphone
  };
}


var buffer_count = 0
var buffer_arry = new Int32Array()

function registerMircophone() {

  navigator.mediaDevices.getUserMedia({ audio: true })
.then(stream => {
  const audioContext = new AudioContext({sampleRate: 16000, blockSize: 400});
  const micSource = audioContext.createMediaStreamSource(stream);

  audioContext.audioWorklet.addModule('./static/processor.js')
    .then(() => {
      const micProcessor = new AudioWorkletNode(audioContext, 'my-worklet-processor');
      micProcessor.port.onmessage =  ({ data }) => {
        var myData = data.outputData;

        buffer_arry = combinedArray = new Int32Array([
          ...buffer_arry,
          ...myData,
        ]);
        buffer_count += 1;

        if (buffer_count == 10) {
          //10 times 400 samples is 0.25s with 16kHz sample rate
          fetch("/recieve_audio", {
            method: "POST",
            body: buffer_arry,
          });

          buffer_count = 0;
          buffer_arry = new Int32Array();
        }
      };
      micSource.connect(micProcessor);
      micProcessor.connect(audioContext.destination);
    });
  });
}

micro_btn.addEventListener("click", async () => {
  registerMircophone()
});

const call_btn = document.getElementById("call_btn");
call_btn.addEventListener("click", async () => {

  const data = { text_input: "dummyInput just for now TODO: change this pls" };
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  };

  fetch('/start_call', options)
    .then(response => {
      console.log("call started")
      registerMircophone()
      registerAudioPlayBackStream()
    })
    .catch(error => console.error(error));
});