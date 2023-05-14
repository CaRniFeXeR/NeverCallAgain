<template>
  <div
    v-if="div_display_state === 0"
    class="grid-container"
    style="position: fixed; width: 95%; top: 17px"
  >
    <div class="grid-item" style="display: flex">
      <div style="width: 70%">
        <h2 style="position: relative; left: 60px">Call Management</h2>
      </div>
      <div style="width: 30%"></div>
    </div>
    <div class="grid-item" style="height: 10px"></div>
    <div class="grid-item" style="height: 30px">
      <input
        type="text"
        v-model="inputText"
        @input="filtercalls"
        style="position: relative; width: 95%; height: 100%"
        placeholder="Search for call"
      />
    </div>
    <CardDiv :calls="calls_to_display" style="height: 500px; margin-top: 10px">
    </CardDiv>

    <AddCardButton
      @create-call="displayCreateCallComponent"
      ButtonTitle="Create new Call"
    />
  </div>

  <CreateCall
    v-if="div_display_state === 1"
    @create-call="createCall"
    @save-call="onlySaveCall"
  ></CreateCall>

  <Slide right :closeOnNavigation="true">
    <a id="home" href="#">
      <span>Home</span>
    </a>
    <a id="Initiator_management" href="#">
      <span>Initiator management</span>
    </a>
    <a id="Receiver_management" href="#">
      <span>Receiver management</span>
    </a>
  </Slide>
</template>

<script>
import axios from "axios";
import CardDiv from "./components/CardDiv.vue";
import AddCardButton from "./components/AddCardButton.vue";
import CreateCall from "./components/CreateCall.vue";
import { Slide } from "vue3-burger-menu";
import Call from "./models/Call";

// border: 1px solid black;
let micProcessor = null;

export default {
  name: "App",
  components: {
    Slide,
    CardDiv,
    AddCardButton,
    CreateCall,
  },
  data() {
    return {
      inputText: "",
      globalAudioCtx: null,
      //manages which div / components are currently getting displayed
      // 0 = display call overview; 1 = display call creation
      div_display_state: 0,

      //state: 0 = not rdy; 1 = pending; 2 = retrieved
      calls: [],
      calls_to_display: Array,
    };
  },
  async created() {
    await this.fetchCalls();
    this.calls_to_display = this.calls;
  },

  methods: {
    filtercalls() {
      if (
        this.inputText != null &&
        this.inputText != "" &&
        this.inputText != " "
      ) {
        const filteredList = this.calls.filter((obj) =>
          obj.title.toLowerCase().startsWith(this.inputText.toLowerCase())
        );
        this.calls_to_display = filteredList;
      } else {
        this.calls_to_display = this.calls;
      }
    },

    displayCreateCallComponent() {
      this.div_display_state = 1;
    },

    async fetchCalls() {
      try {
        const response = await axios.get("/calls");
        const callData = response.data;
        const calls = callData.map((callJson) => {
          const callObj = JSON.parse(callJson);
          return new Call(
            callObj.title,
            parseInt(callObj.state),
            callObj.receiverName,
            callObj.receiverPhonenr,
            callObj.initiatorName,
            callObj.possibleDatetimes,
            callObj.result
          );
        });
        this.calls = calls;
        this.calls_to_display = this.calls;
      } catch (error) {
        console.error(error);
      }
    },

    async createCall(call) {
      this.div_display_state = 0;

      const options = {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(call),
      };

      await fetch("/start_call", options)
        .then((response) => {
          console.log("started call");
          this.registerAudioPlayBackStream();
          this.registerMircophone();
        })
        .catch((error) => console.error(error));

      await this.fetchCalls();

      return;
    },

    onlySaveCall(call) {
      this.div_display_state = 0;
      this.calls.push(call);
      this.calls_to_display = this.calls;
    },

    registerAudioPlayBackStream() {
      var div = document.getElementById("audio_container");

      div.innerHTML = `
        <audio controls="" id="audio_ctrl">
        <source id="audio_src" type="audio/x-wav" sampleRate=22050 src="/stream_audio">
        </audio>  
      `;

      const audio = document.getElementById("audio_ctrl");

      // Wait until the audio is loaded and ready to play
      audio.addEventListener("canplay", function () {
        console.log("can play");
        audio.play();
      });
    },
    registerMircophone() {
      navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
        const audioContext = new AudioContext({ sampleRate: 16000 });

        const micSource = audioContext.createMediaStreamSource(stream);

        audioContext.audioWorklet
          .addModule("./static/processor.js")
          .then(() => {
            const micProcessor = new AudioWorkletNode(
              audioContext,
              "my-worklet-processor"
            );
            micProcessor.port.onmessage = ({ data }) => {
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
    },
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

.bm-burger-button {
  position: fixed;
  width: 36px;
  height: 30px;
  left: auto;
  right: 36px;
  top: 36px;
  cursor: pointer;
}
</style>
