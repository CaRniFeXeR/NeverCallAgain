<template>
    <button @click="emitEvent" class="addCardBtn">{{ButtonTitle}}</button>
</template>

<script>

export default{
    name: "AddCardButton",
    props: {
        ButtonTitle: String
    },
    methods: {
      emitEvent(){
        this.$emit('create-call', 'testparam1', 'testparam2');
      },
    }
}

</script>

<style scoped>



/* CSS */
.addCardBtn {
    margin-top: 10px;
  background-color: #e1ecf4;
  border-radius: 3px;
  border: 1px solid #7aa7c7;
  box-shadow: rgba(255, 255, 255, .7) 0 1px 0 0 inset;
  box-sizing: border-box;
  color: #39739d;
  cursor: pointer;
  display: inline-block;
  font-family: -apple-system,system-ui,"Segoe UI","Liberation Sans",sans-serif;
  font-size: 17px;
  font-weight: 400;
  line-height: 1.15385;
  outline: none;
  padding: 8px .8em;
  position: relative;
  text-align: center;
  text-decoration: none;
  user-select: none;
  -webkit-user-select: none;
  touch-action: manipulation;
  vertical-align: baseline;
  white-space: nowrap;
  width: 300px;
  height: 50px;
}

.addCardBtn:hover,
.addCardBtn:focus {
  background-color: #b3d3ea;
  color: #2c5777;
}

.addCardBtn:focus {
  box-shadow: 0 0 0 4px rgba(0, 149, 255, .15);
}

.addCardBtn:active {
  background-color: #a0c7e4;
  box-shadow: none;
  color: #2c5777;
}

</style>