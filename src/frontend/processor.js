// This is "processor.js" file, evaluated in AudioWorkletGlobalScope upon
// audioWorklet.addModule() call in the main global scope.
class MyWorkletProcessor extends AudioWorkletProcessor {
    constructor() {
      super();
      this.port.onmessage = this.handleMessage.bind(this);
      this.buffer_count = 0
      this.buffer_arry = new Int32Array()
    }

    handleMessage(event) {
        console.log("message from main thread recieved")
      }
  
      process(inputs, outputs) {
        const data = inputs[0][0]
        const inputBuffer = inputs[0][0];

        // Create a new Int32Array for the output data
        const outputData = new Int32Array(data.length);

        // Convert the input audio data to signed int32
        for (let i = 0; i < inputBuffer.length; i++) {
        // Scale the audio data from -1 to 1 to the full range of a signed int32 value (-2147483648 to 2147483647)
        outputData[i] = Math.floor(inputBuffer[i] * 2147483647);
        }

        this.buffer_arry = new Int32Array([
          ...this.buffer_arry,
          ...outputData,
        ]);
        this.buffer_count += 1;

        if (this.buffer_count == 120) {
          //40 times 128 samples is 0.32s with 16kHz sample rate
          //100 times 128 samples is 0.8s with 16kHz sample rate
          const audio_segement = this.buffer_arry
          this.port.postMessage({audio_segement})
          console.log("send audio of size" + audio_segement.length)
          this.buffer_arry = new Int32Array();
          this.buffer_count = 0;
        }
        return true;
      }
  }
  
  registerProcessor('my-worklet-processor', MyWorkletProcessor);