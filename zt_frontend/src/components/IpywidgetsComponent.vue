<template>
  <v-container>
    <div :id="id"></div>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref, watch } from 'vue';
import * as base from '@jupyter-widgets/base';
import * as htmlManager from '@jupyter-widgets/html-manager';

export default defineComponent({
  props: {
    id: {
      type: String,
      required: true,
    },
    widget: {
      type: Object as () => { 'application/vnd.jupyter.widget-view+json': { version_major: number, model_id: string } },
      required: true,
    },
  },
  setup(props) {
    const manager = ref(new htmlManager.HTMLManager());

    const displayWidget = async () => {
      const widgetData = props.widget['application/vnd.jupyter.widget-view+json'];
      console.log(widgetData);
      if (widgetData && widgetData.version_major === 2) {
        if (await manager.value.has_model(widgetData.model_id)) {
          const model = await manager.value.get_model(widgetData.model_id);
          if (model) {
            const widgetContainer = document.getElementById(props.id);
            if (widgetContainer) {
              const view = await manager.value.create_view(model);
              widgetContainer.appendChild(view.el);
              manager.value.display_view(view, widgetContainer);
            }
          }
        }
      }
    };

    // Reactively watch for changes in the widget prop and re-display the widget
    watch(() => props.widget, displayWidget, { immediate: true });

    onMounted(() => {
      displayWidget();
    });

    return {
      manager,
    };
  },
});
</script>

<style scoped>
/* Styles for the widget container */
.v-container {
  overflow: hidden; /* Adjust based on your layout needs */
}
</style>
