<template>
  <div v-if="call" class="card">
    <div :class="headerClass">
      {{ call.title }}
    </div>
    <div class="card-body">
      <p class="card-body-text"><b>From:</b> {{ call.initiatorName }}</p>
      <p class="card-body-text"><b>To:</b> {{ call.receiverName }}</p>
      <p v-if="call.state == 2">
        <b>Appointed at: {{ call.result }}</b>
      </p>
    </div>
  </div>
</template>

<script>
import Call from "../models/Call";

export default {
  name: "CallCard",
  props: {
    call: {
      type: Call,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    state: {
      type: Number,
      default: 0,
    },
  },
  computed: {
    headerClass() {
      switch (this.state) {
        case 1:
          return "card-header card-header-blue";
        case 2:
          return "card-header card-header-green";
        default:
          return "card-header card-header-grey";
      }
    },
  },
};
</script>
<style>
.card {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0px 0px 10px #ccc;
  display: flex;
  flex-direction: column;
  height: 200px;
  width: 45%;
  margin-left: 7px;
  margin-bottom: 5px;
}

.card-header {
  font-size: 20px;
  font-weight: bold;
  padding: 10px;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
}

.card-header-grey {
  background-color: grey;
  color: white;
}

.card-header-blue {
  background-color: #007bff;
  color: white;
}

.card-header-green {
  background-color: green;
  color: white;
}

.card-body {
  flex-grow: 1;
  padding: 3px;
  overflow-y: auto;
}

.card-body-text {
  margin-top: 5px;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: left;
}
</style>
