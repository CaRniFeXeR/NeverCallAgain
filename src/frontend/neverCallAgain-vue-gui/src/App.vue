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
      <p>This is some additional content for the card body.</p>
    </CardDiv>

    <AddCardButton
      @create-call="displayCreateCallComponent"
      ButtonTitle="Create new Call"
    />
  </div>

  <CreateCall
    v-if="div_display_state === 1"
    @create-call="createCall"
  ></CreateCall>

  <!-- Slide has to be beneath grid in order to be clickable
  https://github.com/mbj36/vue-burger-menu
  -->
  <Slide right :closeOnNavigation="true" width="300">
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

// border: 1px solid black;

export default {
  name: "App",
  components: {
    Slide,
    // CardDiv,
    CardDiv,
    AddCardButton,
    CreateCall,
  },
  data() {
    return {
      inputText: "",

      //manages which div / components are currently getting displayed
      // 0 = display call overview; 1 = display call creation
      div_display_state: 0,

      //state: 0 = not rdy; 1 = pending; 2 = retrieved
      calls: [
        {
          id: "1",
          title: "call",
          state: 0,
        },

        {
          id: "2",
          title: "calll",
          state: 1,
        },

        {
          id: "3",
          title: "callll",
          state: 2,
        },

        {
          id: "4",
          title: "calllll",
          state: 0,
        },

        {
          id: "5",
          title: "callllll",
          state: 0,
        },

        {
          id: "6",
          title: "calllllll",
          state: 0,
        },

        {
          id: "7",
          title: "CallTitle_7",
          state: 0,
        },

        {
          id: "8",
          title: "CallTitle_8",
          state: 0,
        },
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
      console.log("craete new profile");
    },

    createCall(param) {
      console.log("create call with param: ", param);
      this.div_display_state = 0;
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
