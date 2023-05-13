// This is "processor.js" file, evaluated in AudioWorkletGlobalScope upon
// audioWorklet.addModule() call in the main global scope.
class MyWorkletProcessor extends AudioWorkletProcessor {
    constructor() {
      super();
      this.port.onmessage = this.handleMessage.bind(this);
    }

    handleMessage(event) {
        // const inputBuffer = event.data;
        // const audioData = inputBuffer.getChannelData(0);
        // const xhr = new XMLHttpRequest();
        // xhr.open('POST', '/audio', true);
        console.log("print")
        // xhr.send(audioData);
      }
  
      process(inputs, outputs) {
        console.log("process audio")
        const data = inputs[0][0]

        const inputBuffer = inputs[0][0];

        // Create a new Int32Array for the output data
        const outputData = new Int32Array(data.length);

        // Convert the input audio data to signed int32
        for (let i = 0; i < inputBuffer.length; i++) {
        // Scale the audio data from -1 to 1 to the full range of a signed int32 value (-2147483648 to 2147483647)
        outputData[i] = Math.floor(inputBuffer[i] * 2147483647);
        }

        
        this.port.postMessage({outputData})
        return true;
      }
  }
  
  registerProcessor('my-worklet-processor', MyWorkletProcessor);