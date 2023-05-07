const form = document.getElementById('myForm');

form.addEventListener('submit', function(event) {
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

btn.onclick = function() {
  var div = document.getElementById("audio_container")

  div.innerHTML = `
    <audio controls="">
    <source id="audio_src" type="audio/x-wav" sampleRate=22050 src="/stream_audio">
    </audio>  
  `

  // var audio_src = document.getElementById("audio_src")
  // audio_src.src = '/stream_audio'
}



// var audio = new Audio('/stream_audio');
// audio.play();