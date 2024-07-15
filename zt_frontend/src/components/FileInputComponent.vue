<template>
    <v-file-input
      label="Upload File"
      @change="handleFileUpload"
    ></v-file-input>
  </template>
  
  <script>
  export default {
    methods: {
      handleFileUpload(file) {
        console.log(file); // process the file
      }
    }
  }
  </script>
  