<template>
    <v-container>
      <div :id="id"></div>
    </v-container>
  </template>
  
  <script lang="ts">
import { defineComponent, onMounted, ref, watch } from 'vue';
// Import your custom WidgetManager instead of the htmlManager.HTMLManager
import { WidgetManager } from './WidgetManager';

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
    // Initialize your custom WidgetManager with the container element
    const manager = ref<WidgetManager|null>(null);
    const displayWidget = async () => {
      const widgetData = props.widget['application/vnd.jupyter.widget-view+json'];
      if (widgetData && widgetData.version_major === 2) {
        const widgetContainer = document.getElementById(props.id);
        if (widgetContainer && !manager.value) {
          // Create a new instance of WidgetManager with the widget container
          manager.value = new WidgetManager(widgetContainer);
        }
        if (manager.value) {
          // Assuming your WidgetManager class has methods to handle model loading and view creation
          console.log(await manager.value.has_model(widgetData.model_id));
          if (await manager.value.has_model(widgetData.model_id)) {
            const model = await manager.value.get_model(widgetData.model_id);
            console.log(model);
            if (model) {
              // Here we assume your WidgetManager's create_view and display_view methods work similarly to htmlManager's
              const view = await manager.value.create_view(model);
              // This might be redundant if your WidgetManager's display_view already appends the view to the container
              widgetContainer?.appendChild(view.el);
              await manager.value.display_view(view);
            }
          }
        }
      }
    };
    // Reactively watch for changes in the widget prop and re-display the widget
    watch(() => props.widget, displayWidget, { immediate: true });
    onMounted(displayWidget);
    return {
      manager,
    };
  },
});
</script>