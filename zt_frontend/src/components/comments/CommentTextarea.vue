<template>
  <div class="d-flex flex-column" style="flex: 1" ref="commentEditContainer">
    <v-textarea
      :model-value="modelValue"
      ref="commentEditTextArea"
      @update:model-value="(val) => emit('update:modelValue', val)"
      variant="outlined"
    ></v-textarea>
    <div class="d-flex justify-end">
      <v-btn variant="text" @click="emit('cancel')">Cancel</v-btn>
      <v-btn
        color="primary"
        class="ml-2"
        :loading="isSaving"
        :disabled="!modelValue || isSaving"
        @click="emit('submit')"
        >Submit</v-btn
      >
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  isSaving: Boolean,
  modelValue: String,
});

const commentEditTextArea = ref<HTMLElement | null>(null);
const commentEditContainer = ref<HTMLElement | null>(null);

onMounted(() => {
  // Scroll the component into view
  commentEditContainer.value?.scrollIntoView({
    behavior: "smooth",
    block: "nearest",
    inline: "start",
  });

  // Autofocus the textarea
  commentEditTextArea.value?.focus();
});

const emit = defineEmits(["cancel", "submit", "update:modelValue"]);
</script>

<style lang="scss" scoped></style>
