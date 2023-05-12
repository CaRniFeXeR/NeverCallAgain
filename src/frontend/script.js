const form = document.getElementById('myForm');
form.addEventListener('submit', function (event) {
  event.preventDefault(); // prevent the default form submission behavior

  const input = document.getElementById('text_input');
  const inputValue = input.value;

  const data = { text_input: inputValue };
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  };

  fetch('/submit', options)
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error(error));
});


// onclick button with id audio_click

const btn = document.getElementById("audio_btn")

btn.onclick = function () {
  var div = document.getElementById("audio_container")

  div.innerHTML = `
    <audio controls="">
    <source id="audio_src" type="audio/x-wav" sampleRate=22050 src="/stream_audio">
    </audio>  
  `

  // var audio_src = document.getElementById("audio_src")
  // audio_src.src = '/stream_audio'
}

const micro_btn = document.getElementById("micro_btn")

function handleMicStream(streamObj) {
  // keep the context in a global variable
  stream = streamObj;

  input = audioContext.createMediaStreamSource(stream);

  input.connect(processor);

  processor.onaudioprocess = e => {
    microphoneProcess(e); // receives data from microphone
  };
}


function microphoneProcess(e) {
  const left = e.inputBuffer.getChannelData(0); // get only one audio channel
  const left16 = convertFloat32ToInt16(left); // skip if you don't need this
  socket.emit('micBinaryStream', left16); // send to server via web socket
}

// Converts data to BINARY16
function convertFloat32ToInt16(buffer) {
  let l = buffer.length;
  const buf = new Int16Array(l / 3);

  while (l--) {
    if (l % 3 === 0) {
      buf[l / 3] = buffer[l] * 0xFFFF;
    }
  }
  return buf.buffer;
}



let stream;

micro_btn.addEventListener("click", async () => {
  // Prompt the user to use their microphone.
  stream = await navigator.mediaDevices.getUserMedia({
    audio: true,
  });
  const context = new AudioContext();
  const source = context.createMediaStreamSource(stream);

  const mediaRecorder = new MediaRecorder(source.mediaStream);
  

  const socket = new WebSocket('ws://172.20.224.125:5000/recieve_audio_input');

  socket.addEventListener('open', function(event) {
    console.log('Connected!');

    mediaRecorder.addEventListener('dataavailable', event => {
      const reader = new FileReader();
      reader.readAsDataURL(event.data);
      print("data available")
      reader.onloadend = () => {
        const base64data = reader.result.split(',')[1];
        socket.emit('audio_chunk', base64data);
      };
    });
    mediaRecorder.start(1000);
});



});

  // Load and execute the module script.
  // await context.audioWorklet.addModule("processor.js");
  // // Create an AudioWorkletNode. The name of the processor is the
  // // one passed to registerProcessor() in the module script.
  // const processor = new AudioWorkletNode(context, "processor");

  // source.connect(processor).connect(context.destination);
// });

// stopMicrophoneButton.addEventListener("click", () => {
//   // Stop the stream.
//   stream.getTracks().forEach(track => track.stop());

//   log("Your microphone audio is not used anymore.");
// });
  