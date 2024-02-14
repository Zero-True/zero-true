<template>
  <div :id="id" style="height: 100%; width: 100%">
    <!-- Plotly plot will be rendered here -->
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, onUnmounted, PropType } from 'vue';
import Plotly from "plotly.js-dist-min";


export default defineComponent({
  props: {
    figureJson: {
      type: String,
      required: true,
    },
    id: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const resizePlot = () => {
      const plotElement = document.getElementById(props.id);
      if (plotElement) {
        Plotly.Plots.resize(plotElement);
      }
    };

    // Initial plot rendering and responsive resize
    onMounted(() => {
      const figure = JSON.parse(props.figureJson);
      Plotly.newPlot(props.id, figure.data, figure.layout).then(() => {
        window.addEventListener('resize', resizePlot);
      });
    });

    // Cleanup on component unmount
    onUnmounted(() => {
      window.removeEventListener('resize', resizePlot);
    });
  },
});
</script>
