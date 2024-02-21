<template></template>
<script lang="ts">
import { defineComponent } from "vue";
import { Timer } from "@/timer";
import { globalState } from "@/global_vars";

export default defineComponent({
  name: "TimerComponent",
  props: {
    interval: {
      type: Number,
      required: true,
    },
    id: {
      type: String,
      required: true,
    },
    value: {
      type: Boolean,
      default: false,
    },
  },
  created() {
    const startTimer = () => {
      const timer = new Timer(this.interval);
      globalState.timers[this.id] = timer;
      timer.start(startTimer);
      this.$emit('click');
    };

    if (!globalState.timers[this.id]) {
      const timer = new Timer(this.interval);
      globalState.timers[this.id] = timer;
      timer.start(startTimer);
    }
  },
  unmounted() {
    const timer = globalState.timers[this.id];
    if (timer) {
      timer.stop();
      delete globalState.timers[this.id]; 
    }
  },
});
</script>
