let globalAudioCtx = null

// onclick button with id audio_click
const btn = document.getElementById("audio_btn");

function registerAudioPlayBackStream() {
  var div = document.getElementById("audio_container")

  div.innerHTML = `
    <audio controls="" id="audio_ctrl">
    <source id="audio_src" type="audio/x-wav" sampleRate=22050 src="/stream_audio">
    </audio>  
  `

  const audio = document.getElementById("audio_ctrl");

  // Wait until the audio is loaded and ready to play
  audio.addEventListener("canplay", function() {
    console.log("can play")
    audio.play();
  });
}

btn.onclick = function () {
  registerAudioPlayBackStream()
}

const micro_btn = document.getElementById("micro_btn");

function registerMircophone() {

  navigator.mediaDevices.getUserMedia({ audio: true })
.then(stream => {
  const audioContext = new AudioContext({sampleRate: 16000});

  const micSource = audioContext.createMediaStreamSource(stream);
  globalAudioCtx = audioContext


  audioContext.audioWorklet.addModule('./static/processor.js')
    .then(() => {
      micProcessor = new AudioWorkletNode(audioContext, 'my-worklet-processor');
      micProcessor.port.onmessage =  ({ data }) => {
        var myData = data.audio_segement;

        // console.log("recieved data of" + myData.length)
        
        fetch("/recieve_audio", {
          method: "POST",
          body: myData,
        });

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

const close_btn = document.getElementById("close_btn");
close_btn.addEventListener("click", async () => {

  var div = document.getElementById("audio_container")

  div.innerHTML = `` //remove audio element
  if (globalAudioCtx != null){
    globalAudioCtx.audioWorklet.removeModule("./static/processor.js") //remove microphone listener
  }

  const data = { text_input: "close request" };
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  };

  fetch('/reset_conv', options)
    .then(response => {
      console.log("call reseted")
    })
    .catch(error => console.error(error));
});