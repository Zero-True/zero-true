<template>
  <div :id="id" style="height: 100%; width: 100%">
    <!-- Plotly plot will be rendered here -->
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, onUnmounted, PropType, watch } from 'vue';
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

    // Function to render or update the plot
    const renderPlot = (figureJson: string) => {
      const figure = JSON.parse(figureJson);
      Plotly.react(props.id, figure.data, figure.layout);
    };

    // Initial plot rendering and responsive resize
    onMounted(() => {
      renderPlot(props.figureJson);
      window.addEventListener('resize', resizePlot);
    });

    // Cleanup on component unmount
    onUnmounted(() => {
      window.removeEventListener('resize', resizePlot);
    });

    // Watch for changes in figureJson prop and update the plot
    watch(() => props.figureJson, (newFigureJson) => {
      renderPlot(newFigureJson);
    });
  },
});
</script>
