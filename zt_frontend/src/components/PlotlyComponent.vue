<template>
    <div id="plotly-plot" style="height: 100%; width: 100%;">
      <!-- Plotly plot will be rendered here -->
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, PropType, onMounted } from 'vue';
  import Plotly from "plotly.js-basic-dist";
  
  export default defineComponent({
    props: {
      figure: {
        type: Object as PropType<any>,
        required: true,
      },
      layout: {
        type: Object as PropType<any>,
        required: true,
      },
    },
    setup(props) {
      onMounted(() => {
        Plotly.newPlot('plotly-plot', props.figure.data, props.layout);

      });
    },
  });
  </script>
  