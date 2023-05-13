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

btn.onclick = function () {
  var div = document.getElementById("audio_container");

  div.innerHTML = `
    <audio controls="">
    <source id="audio_src" type="audio/x-wav" sampleRate=22050 src="/stream_audio">
    </audio>  
  `;

  // var audio_src = document.getElementById("audio_src")
  // audio_src.src = '/stream_audio'
};

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

function microphoneProcess(e) {
  const left = e.inputBuffer.getChannelData(0); // get only one audio channel
  const left16 = convertFloat32ToInt16(left); // skip if you don't need this
  socket.emit("micBinaryStream", left16); // send to server via web socket
}

// Converts data to BINARY16
function convertFloat32ToInt16(buffer) {
  let l = buffer.length;
  const buf = new Int16Array(l / 3);

  while (l--) {
    if (l % 3 === 0) {
      buf[l / 3] = buffer[l] * 0xffff;
    }
  }
  return buf.buffer;
}

let stream;

let socket = null;

// micro_btn.addEventListener("click", async () => {
//   // Prompt the user to use their microphone.
//   stream = await navigator.mediaDevices.getUserMedia({
//     audio: true,

//   });
//   const context = new AudioContext({sampleRate: 16000});
//   const source = context.createMediaStreamSource(stream);

//   const mediaRecorder = new MediaRecorder(source.mediaStream); //, options = {mimeType :'audio/ogg'});
//   console.log('Connected!');
//   mediaRecorder.start(1000);

//   mediaRecorder.addEventListener('dataavailable', event => {
//     console.log("data available")
//     var data = new FormData()
//     data.append('file', event.data , 'file')
//     fetch('http://172.20.224.125:5000/recieve_audio', {
//           method: 'POST',
//           body: data

//       }).then(response => response.json()
//       ).then(json => {
//           console.log(json)
//       });
//     // const reader = new FileReader();
//     // reader.readAsDataURL(event.data);
//     // reader.onloadend = () => {
//     //   const base64data = reader.result.split(',')[1];
//     //   socket.emit('audio_chunk', base64data);
//     // };
//   });

// //   const socket = new WebSocket('ws://172.20.224.125:5000/recieve_audio_input');

// //   socket.addEventListener('open', function(event) {

// // });

// });

var buffer_count = 0;
var buffer_arry = new Int32Array();

micro_btn.addEventListener("click", async () => {
  navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
    const audioContext = new AudioContext({ sampleRate: 16000 });
    const micSource = audioContext.createMediaStreamSource(stream);

    audioContext.audioWorklet.addModule("./static/processor.js").then(() => {
      const micProcessor = new AudioWorkletNode(
        audioContext,
        "my-worklet-processor"
      );
      micProcessor.port.onmessage = ({ data }) => {
        // debugger;
        // socket.send(data.data)
        // socket.emit('my event', {data: 'I\'m connected!2'});
        // buffer_list.push(data.data)
        var myData = data.outputData;

        buffer_arry = combinedArray = new Int32Array([
          ...buffer_arry,
          ...myData,
        ]);
        buffer_count += 1;

        if (buffer_count == 500) {
          fetch("/recieve_audio2", {
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

  // socket = new WebSocket('ws://172.20.224.125:5000/recieve_audio_input')

  // // buffer_list = []s

  // // Add an event listener to handle incoming messages
  // socket.addEventListener('message', (event) => {
  //   console.log(`Received message: ${event.data}`);
  // });

  // // Add an event listener to handle connection close
  // socket.addEventListener('close', (event) => {
  //   console.log('WebSocket connection closed');
  // });

  // // Add an event listener to handle errors
  // socket.addEventListener('error', (event) => {
  //   console.log(`WebSocket error: ${event}`);
  // });

  // socket.addEventListener('open', function(event) {
  //   console.log('Connected!');
  //   // socket.send("sdfsdfsdf")
  //   // socket.emit('my event', {data: 'I\'m connected!'});

  // });

  // navigator.getUserMedia({ audio: true },
  //   function (e) {
  //       // creates the audio context
  //       window.AudioContext = window.AudioContext || window.webkitAudioContext;
  //       context = new AudioContext();

  //       // creates an audio node from the microphone incoming stream
  //       mediaStream = context.createMediaStreamSource(e);

  //       // https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/createScriptProcessor
  //       var bufferSize = 2048;
  //       var numberOfInputChannels = 2;
  //       var numberOfOutputChannels = 2;
  //       if (context.createScriptProcessor) {
  //           recorder = context.createScriptProcessor(bufferSize, numberOfInputChannels, numberOfOutputChannels);
  //       } else {
  //           recorder = context.createJavaScriptNode(bufferSize, numberOfInputChannels, numberOfOutputChannels);
  //       }

  //       recorder.onaudioprocess = function (e) {
  //           console.log("on audio progress");
  //       }

  //       // we connect the recorder with the input stream
  //       mediaStream.connect(recorder);
  //       recorder.connect(context.destination);

  //     });
});
