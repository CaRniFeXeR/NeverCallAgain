<template>
  <div
    v-if="div_display_state === 0"
    class="grid-container"
    style="position: fixed; width: 95%; top: 17px"
  >
    <div class="grid-item" style="display: flex">
      <div style="width: 70%">
        <h2>Call Management</h2>
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
import CardDiv from "./components/CardDiv.vue";
import AddCardButton from "./components/AddCardButton.vue";
import CreateCall from "./components/CreateCall.vue";
import { Slide } from "vue3-burger-menu";
import Call from "./models/Call";

// border: 1px solid black;

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
      baseUrlBackend: "http://localhost:5000/",

      //manages which div / components are currently getting displayed
      // 0 = display call overview; 1 = display call creation
      div_display_state: 0,

      //state: 0 = not rdy; 1 = pending; 2 = retrieved
      calls: [
        new Call(
          "Test call",
          2,
          "Dr. Palkovits",
          "01234 110101010",
          "Werner Faymann",
          [
            {
              selectedDate: "03.02.2032",
              selectedStartTime: "08:00",
              selectedEndTime: "10:00",
            },
          ],
          "21.05.2023, 14:00"
        ),
      ],
      calls_to_display: Array,
    };
  },
  created() {
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
      console.log("create new call");
    },

    async createCall(call) {
      console.log("schedule appointment with param: ", call);
      this.div_display_state = 0;
      this.calls.push(call);
      this.calls_to_display = this.calls;

      let url = this.baseUrlBackend + "start_call";

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(call),
      });

      return response;
    },

    onlySaveCall(call) {
      this.div_display_state = 0;
      this.calls.push(call);
      this.calls_to_display = this.calls;
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
