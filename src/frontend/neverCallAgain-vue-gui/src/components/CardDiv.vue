<template>
  <div class="card-div" style="overflow-y: auto">
    <CallCard
      v-for="item in calls"
      :key="item.id"
      :call="item"
      :title="item.title"
      :state="item.state"
    >
      <slot></slot>
    </CallCard>
  </div>
</template>

<script>
import CallCard from "./Card.vue";

export default {
  name: "CardDiv",
  props: {
    calls: {
      type: Array,
      required: true,
    },
  },
  components: {
    CallCard,
  },
};
</script>

<style scoped>
.card-div {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px;
  border: 3px solid lightgrey;
  border-radius: 5px;
}
</style>
