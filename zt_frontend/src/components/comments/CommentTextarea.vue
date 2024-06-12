<template>
  <v-textarea
    :model-value="modelValue" 
    @update:model-value="val => emit('update:modelValue', val)" 
    variant="outlined" 
  ></v-textarea>
  <div class="d-flex justify-end">
    <v-btn
      variant="text"
      @click="emit('cancel')"
    >Cancel</v-btn>
    <v-btn 
      color="primary" 
      class="ml-2"
      :loading="isSaving"
      :disabled="!modelValue || isSaving" 
      @click="emit('submit')"   
    >Submit</v-btn>
  </div> 
</template>

<script setup lang="ts">

defineProps({
  isSaving: Boolean,
  modelValue: String
})

const emit = defineEmits(['cancel', 'submit', 'update:modelValue'])
</script>

<style lang="scss" scoped>
</style>
