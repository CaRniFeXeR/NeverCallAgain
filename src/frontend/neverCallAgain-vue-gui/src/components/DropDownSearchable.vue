<template>
    <div class="dropdown">
      <input type="text" v-model="searchTerm" @input="filterOptions" @click="showDropdownFunction" ref="input" :class="{ error: isInputInvalid }" />
      <ul :class="{show: filteredOptions.length > 0}" v-show="showDropdown" ref="dropdown">
        <li v-for="(option, index) in filteredOptions" :key="index" @click="selectOption(option)">
          {{ option }}
        </li>
      </ul>
    </div>
  </template>
  <script>
  export default {
    name: "SearchableDropdown",
    props: {
      options: {
        type: Array,
        required: true,
      },
    },
    data() {
      return {
        searchTerm: '',
        showDropdown: false,
        selectedOption: null,
      };
    },
    computed: {
      filteredOptions() {
        return this.options.filter(option => option.toLowerCase().includes(this.searchTerm.toLowerCase()));
      },
      isInputInvalid() {
        return this.searchTerm !== '' && this.filteredOptions.indexOf(this.searchTerm) === -1;
      }
    },
    methods: {
      filterOptions(event) {
        this.searchTerm = event.target.value;
      },
      selectOption(option) {
        this.selectedOption = option;
        this.searchTerm = option;
        this.showDropdown = false;
        this.$emit('selected', option);
      },
      showDropdownFunction() {
        this.showDropdown = true;
        this.$nextTick(() => {
          this.$refs.dropdown.style.width = `${this.$refs.input.clientWidth}px`;
        });
      },
    },
  };
  </script>
  <style scoped>
  .dropdown {
    position: relative;
    display: inline-block;
  }

.dropdown input[type="text"] {
width: 100%;
padding: 8px;
border: 1px solid #ccc;
border-radius: 4px;
}

.dropdown input[type="text"].error {
border-color: orange;
}

.dropdown ul {
position: absolute;
top: 100%;
left: 0;
width: 100%;
max-height: 150px;
overflow-y: auto;
background-color: #fff;
border: 1px solid #ccc;
border-top: none;
border-radius: 4px;
list-style: none;
padding: 0;
margin: 0;
z-index: 1;
display: none;
}

.dropdown ul.show {
display: block;
}

.dropdown li {
padding: 8px 12px;
cursor: pointer;
transition: all 0.2s;
}

.dropdown li:hover {
background-color: #f6f6f6;
}
</style>