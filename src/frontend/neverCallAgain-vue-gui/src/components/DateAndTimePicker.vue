<template>
  <div
    class="datetime-picker"
    style="
      margin-bottom: 10px;
      border: 1px solid black;
      border-radius: 10px;
      padding: 10px;
      position: relative;
    "
  >
    <div
      v-if="isAdditionalDateTime"
      style="position: absolute; top: 0; right: 10px"
    >
      <button
        style="
          background: none;
          border: none;
          padding: 0;
          margin: 0;
          font-size: 20px;
          color: black;
          width: 30px;
          height: 30px;
        "
        @click="$emit('close')"
      >
        X
      </button>
    </div>
    <div class="form-group">
      <label for="datepicker" class="label-for-input">Date:</label>
      <input
        id="datepicker"
        type="date"
        v-model="selectedDate"
        class="input-textfield"
      />
    </div>
    <div class="form-group">
      <label for="starttimepicker" class="label-for-input">From:</label>
      <select
        id="starttimepicker"
        v-model="selectedStartTime"
        class="input-textfield"
      >
        <option v-for="startTime in startTimeOptions" :value="startTime">
          {{ startTime }}
        </option>
      </select>
    </div>

    <div class="form-group">
      <label for="endtimepicker" class="label-for-input">To:</label>
      <select
        id="endtimepicker"
        v-model="selectedEndTime"
        class="input-textfield"
      >
        <option v-for="endTime in endTimeOptions" :value="endTime">
          {{ endTime }}
        </option>
      </select>
    </div>
  </div>
</template>
<script>
export default {
  name: "DateTimePicker",
  props: {
    isAdditionalDateTime: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      selectedDate: "",
      selectedStartTime: "08:00",
      selectedEndTime: "12:00",
      startTimeOptions: [
        "07:00",
        "08:00",
        "09:00",
        "10:00",
        "11:00",
        "12:00",
        "13:00",
        "14:00",
        "15:00",
        "16:00",
        "17:00",
        "18:00",
      ],
      endTimeOptions: [
        "07:00",
        "08:00",
        "09:00",
        "10:00",
        "11:00",
        "12:00",
        "13:00",
        "14:00",
        "15:00",
        "16:00",
        "17:00",
        "18:00",
      ],
    };
  },
  methods: {
    getData() {
      return {
        selectedDate: "",
        selectedStartTime: this.selectedStartTime,
        selectedEndTime: this.selectedEndTime,
      };
    },
  },
};
</script>
<style scoped>
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
</style>
