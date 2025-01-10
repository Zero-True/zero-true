<template>
    <div class="click-edit" v-if="isDevMode && keepCodeInAppModel">
      <div class="click-edit__show-text" v-if="!isEditing">
        <div class="loading-wrapper">
          <v-progress-circular
            v-if="cellId == currentlyExecutingCell && isCodeRunning"
            indeterminate
            size="24"
            class="ml-1 mr-2 green-loader"
          />
        </div>
        <h4
          class="text-bluegrey-darken-1 text-ellipsis click-edit__name"
          @click="toggleEdit"
        >
          {{ modelValue }}
        </h4>
      </div>
  
      <div class="click-edit__edit-field-wrapper" v-if="isEditing">
        <v-text-field
          v-model="editValue"
          :placeholder="cellType"
          density="compact"
          variant="plain"
          hide-details
          ref="cellNameField"
          class="click-edit__edit-field"
          @keydown.enter="save"
          @update:focused="(focused:any) => { if (!focused) save(); }"
        />
      </div>
    </div>
    <h4
      v-else-if="isDevMode"
      class="text-bluegrey-darken-1 text-ellipsis click-edit__static-name"
    >
      {{ modelValue }}
    </h4>
  </template>
  
  <script setup lang="ts">
  import { ref, nextTick } from 'vue';
  import type { VTextField } from "vuetify/lib/components/index.mjs";
  import axios from "axios";
  import { NameCellRequest } from "@/types/name_cell_request";
  
  const props = defineProps({
    modelValue: String,
    isDevMode: Boolean,
    keepCodeInAppModel: Boolean,
    cellId: String,
    cellType: String,
    currentlyExecutingCell: String,
    isCodeRunning: Boolean
  });
  
  const emit = defineEmits(['update:modelValue']);
  
  const isEditing = ref(false);
  const editValue = ref('');
  const cellNameField = ref<VTextField | null>(null);
  
  const toggleEdit = () => {
    isEditing.value = !isEditing.value;
    if (isEditing.value) {
      editValue.value = props.modelValue || '';
      nextTick(() => {
        if (cellNameField.value) {
          cellNameField.value.focus();
        }
      });
    }
  };
  
  const save = async () => {
    const nameCellRequest: NameCellRequest = {
      cellId: props.cellId as string,
      cellName: editValue.value as string,
    };
    await axios.post(import.meta.env.VITE_BACKEND_URL + "api/rename_cell", nameCellRequest);
    emit('update:modelValue', editValue.value);
    isEditing.value = false;
  };
  </script>

<style lang="scss" scoped>
@import '@/styles/cell.scss';
</style>