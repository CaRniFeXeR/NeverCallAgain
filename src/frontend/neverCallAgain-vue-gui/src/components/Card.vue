<template>
  <div class="card">
    <div :class="headerClass">
      {{ title }}
    </div>
    <div class="card-body">
      <slot></slot>
    </div>
  </div>
</template>


<script>
export default {
  name: "CallCard",
  props: {
    title: {
      type: String,
      required: true
    },
    state: {
      type: Number,
      default: 0
    }
  },
  computed: {
    headerClass() {
      switch(this.state) {
        case 1:
          //somehow this didnt work
          return 'card-header card-header-blue';
          //return 'card-header-blue';
        case 2:
          return 'card-header card-header-green';
          //return 'card-header-green';
        default:
          return 'card-header card-header-grey';

      }
    }
  }
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
  margin-bottom: 5px;;
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
  padding: 10px;
  overflow-y: auto;
}
</style> 