<template>
  <div :id="id" style="height: 100%; width: 100%">
    <!-- Plotly plot will be rendered here -->
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType, onMounted, watch } from "vue";
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
    id: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    // Initial plot
    onMounted(() => {
      Plotly.newPlot(props.id, props.figure.data, props.layout);
    });

    // Watch for changes in figure and layout
    watch(
      () => props.figure,
      (newFigure, oldFigure) => {
        if (newFigure !== oldFigure) {
          Plotly.newPlot(props.id, newFigure.data, props.layout);
        }
      },
      { deep: true }
    );

    watch(
      () => props.layout,
      (newLayout, oldLayout) => {
        if (newLayout !== oldLayout) {
          Plotly.newPlot(props.id, props.figure.data, newLayout);
        }
      },
      { deep: true }
    );
  },
});
</script>
