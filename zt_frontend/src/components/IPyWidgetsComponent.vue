<template>
  <v-container>
    <v-row>
      <v-col class="widgetarea"></v-col>
    </v-row>
  </v-container>
</template>

  <script>
import '@jupyter-widgets/controls/css/widgets.css';
import { WidgetManager } from './manager';

export default {
  name: 'CodeViewer',
  props: {
    widget: Object,
  },

  mounted() {
    console.log(this.widget);
    this.initializeWidgetManager();
  },

  methods: {
    initializeWidgetManager() {
      const widgetArea = this.$el.querySelector('.widgetarea');
      const manager = new WidgetManager(widgetArea);

      // Assuming the 'state' from the prop includes the necessary information
      // to fully initialize the widget state.
      const widgetState = this.widget.state;
      console.log(widgetState);
      // Dynamically obtain the model_id from the prop
      const modelId = this.widget.model_id;

      manager.set_state(widgetState) // Use the widget state
        .then((models) =>
          manager.create_view(models.find((element) => element.model_id == modelId))
        )
        .then((view) => manager.display_view(view));
    },
  },
};
</script>
