<template>
  <h2 style="position: relative; width: 95%; top: 20px">Call Creation</h2>
  <div class="create-card-div" style="margin-top: 30px">
    <div class="form-group">
      <label for="call-title" class="label-for-input" style="font-size: 19px"
        >Call title</label
      >
      <input
        id="call-title"
        type="text"
        v-model="call_title"
        @input="checkInputs"
        class="input-textfield"
      />
    </div>
    <div class="form-group">
      <label for="receiver-name" class="label-for-input" style="font-size: 19px"
        >Receiver name (Name of doctor)</label
      >
      <input
        id="receiver-name"
        type="text"
        v-model="receiver_name"
        @input="checkInputs"
        class="input-textfield"
      />
    </div>

    <div class="form-group">
      <label
        for="receiver-telnr"
        class="label-for-input"
        style="font-size: 19px"
        >Receiver phone number</label
      >
      <input
        id="receiver-telnr"
        type="text"
        v-model="receiver_telnr"
        @input="checkInputs"
        class="input-textfield"
      />
    </div>

    <div class="form-group">
      <label
        for="initiator-name"
        class="label-for-input"
        style="font-size: 19px"
        >Initiator name</label
      >
      <input
        id="initiator-name"
        type="text"
        v-model="initiator_name"
        @input="checkInputs"
        class="input-textfield"
      />
    </div>

    <DateTimePicker ref="Datetimepicker"></DateTimePicker>
    <DateTimePicker
      v-if="this.datetimeCount >= 2"
      isAdditionalDateTime="true"
      ref="Datetimepicker_2"
    ></DateTimePicker>
    <DateTimePicker
      v-if="this.datetimeCount >= 3"
      isAdditionalDateTime="true"
      ref="Datetimepicker_3"
    ></DateTimePicker>

    <button
      class="create-btn"
      @click="emitCreateCall"
      ref="createCallBtn"
      :disabled="!allFieldsFilled"
    >
      Create Call
    </button>
  </div>
  <!-- <SearchableDropdown :options="this.options" @selected="onOptionSelected"></SearchableDropdown> -->
</template>
<script>
import SearchableDropdown from "./DropDownSearchable.vue";
import DateTimePicker from "./DateAndTimePicker.vue";

export default {
  name: "CreateCall",
  props: {}, //maybe pass something to validate input somehow? ie avoid duplicates in card titles

  data() {
    return {
      call_title: "",
      receiver_name: "",
      receiver_telnr: "",
      initiator_name: "",
      possibleDates: [],
      datetimeCount: 3,
    };
  },

  computed: {
    allFieldsFilled() {
      return (
        this.call_title &&
        this.receiver_name &&
        this.receiver_telnr &&
        this.initiator_name
      );
    },
  },

  components: {
    SearchableDropdown,
    DateTimePicker,
  },

  methods: {
    emitCreateCall() {
      console.log(this.$refs.Datetimepicker.getData());
      this.$emit("create-call");
    },
    checkInputs() {
      if (this.allFieldsFilled) {
        this.$refs.createCallBtn.removeAttribute("disabled");
      } else {
        this.$refs.createCallBtn.setAttribute("disabled", "true");
      }
    },
    onOptionSelected(option) {
      this.selectedOption = option;
      console.log(option);
    },
  },
};
</script>
<style scoped>
.create-card-div {
  background-color: lightsteelblue;
  border: 3px solid lightblue;
  border-radius: 10px;
  margin-top: 90px;
  padding-top: 10px;
  padding-bottom: 10px;
}

.form-group {
  display: flex;
  margin-bottom: 20px;
  flex-direction: column;
}

.label-for-input {
  margin-bottom: 3px;
  font-weight: bold;
  font-size: 15pt;
}

.input-textfield {
  padding: 10px;
  border-radius: 5px;
  border: 1px solid #ccc;
  font-size: 16px;
}

@media only screen and (max-width: 768px) {
  .label-for-input {
    font-size: 14px;
  }
  .input-textfield {
    font-size: 14px;
  }

  .create-card-div {
    margin-top: 50px;
  }

  h2 {
    font-size: 24px;
    text-align: center;
  }

  .create-btn {
    width: 100%;
    border-style: 1px solid lightgrey;
    font-weight: bold;
    font-size: 22px;
  }
}
</style>
