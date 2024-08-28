<template>
  <v-btn
    color="bluegrey-darken-4"
    icon="mdi-plus"
    @click="openCreateDialog"
  />

  <v-dialog v-model="createDialogVisible" max-width="500px">
    <v-card>
      <v-card-title>Create New Folder or File</v-card-title>
      <v-card-text>
        <v-text-field 
          v-model="newItemName" 
          label="Name" 
          :error-messages="nameError"
          @input="validateName"
        />
        <v-select
          v-model="newItemType"
          :items="itemTypes"
          item-title="text"
          item-value="value"
          label="Type"
        />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="blue-darken-1" @click="closeDialog">Cancel</v-btn>
        <v-btn color="primary" @click="createNewItem" :disabled="!isValid">Create</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-snackbar v-model="showError" color="error" :timeout="3000">
    {{ errorMessage }}
    <template v-slot:actions>
      <v-btn color="white" variant="text" @click="showError = false">Close</v-btn>
    </template>
  </v-snackbar>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';
import axios from 'axios';

export default defineComponent({
  name: 'FileFolderCreator',
  props: {
    currentPath: {
      type: String,
      required: true
    }
  },
  emits: ['item-created'],
  setup(props, { emit }) {
    const createDialogVisible = ref(false);
    const newItemName = ref('');
    const newItemType = ref('folder');
    const itemTypes = [
      { text: 'Folder', value: 'folder' },
      { text: 'File', value: 'file' }
    ];
    const nameError = ref('');
    const showError = ref(false);
    const errorMessage = ref('');

    const isValid = computed(() => newItemName.value.trim() !== '' && nameError.value === '');

    const validateName = () => {
      if (newItemName.value.trim() === '') {
        nameError.value = 'Name cannot be empty';
      } else if (!/^[a-zA-Z0-9_\-. ]+$/.test(newItemName.value)) {
        nameError.value = 'Name contains invalid characters';
      } else {
        nameError.value = '';
      }
    };

    const openCreateDialog = () => {
      createDialogVisible.value = true;
    };

    const closeDialog = () => {
      createDialogVisible.value = false;
      newItemName.value = '';
      newItemType.value = 'folder';
      nameError.value = '';
    };

    const createNewItem = async () => {
      if (!isValid.value) {
        return;
      }

      try {
        const response = await axios.post(
          `${import.meta.env.VITE_BACKEND_URL}api/create_item`,
          {
            path: props.currentPath,
            name: newItemName.value.trim(),
            type: newItemType.value,
          }
        );
        if (response.data.success) {
          emit('item-created');
          closeDialog();
        } else {
          errorMessage.value = `Failed to create ${newItemType.value}: ${response.data.message}`;
          showError.value = true;
        }
      } catch (error) {
        errorMessage.value = `Error creating ${newItemType.value}: ${error}`;
        showError.value = true;
      }
    };

    return {
      createDialogVisible,
      newItemName,
      newItemType,
      itemTypes,
      nameError,
      showError,
      errorMessage,
      isValid,
      openCreateDialog,
      closeDialog,
      createNewItem,
      validateName
    };
  }
});
</script>