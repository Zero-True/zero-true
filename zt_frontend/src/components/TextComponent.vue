<template>
  <div :class="text_type" :style="{ color: color }">
    {{ text }}
  </div>
</template>

<script>
export default {
  props: {
    text: String,
    text_type: String,
    color: String,
  },
}
</script>
