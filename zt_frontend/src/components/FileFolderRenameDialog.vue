<template>
    <div>
      <v-dialog v-model="dialogVisible" max-width="300px">
        <v-card>
          <v-card-title>Rename Item</v-card-title>
          <v-card-text>
            <v-text-field
              v-model="newName"
              label="New Name"
              :rules="[v => !!v || 'Name is required']"
              required
              @keyup.enter="renameItem"
            />
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn color="blue-darken-1" variant="text" @click="closeDialog">Cancel</v-btn>
            <v-btn color="blue-darken-1" variant="text" @click="renameItem" :disabled="!newName">Rename</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
  
      <v-snackbar v-model="showError" color="error" :timeout="5000">
        {{ errorMessage }}
        <template v-slot:actions>
          <v-btn color="white" variant="text" @click="showError = false">
            Close
          </v-btn>
        </template>
      </v-snackbar>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, watch } from 'vue';
  import axios from 'axios';
  
  export default defineComponent({
    name: 'RenameDialog',
    props: {
      currentPath: {
        type: String,
        required: true,
      },
      isProtectedFile: {
        type: Function,
        required: true,
      },
    },
    emits: ['itemRenamed'],
    setup(props, { emit }) {
      const dialogVisible = ref(false);
      const newName = ref('');
      const itemToRename = ref<any>(null);
      const errorMessage = ref('');
      const showError = ref(false);
  
      const openDialog = (item: any) => {
        if (!props.isProtectedFile(item.title)) {
          itemToRename.value = item;
          newName.value = item.title;
          dialogVisible.value = true;
        }
      };
  
      const closeDialog = () => {
        dialogVisible.value = false;
        newName.value = '';
        itemToRename.value = null;
      };
  
      const displayError = (message: string) => {
        errorMessage.value = message;
        showError.value = true;
      };
  
      const renameItem = async () => {
        if (!newName.value.trim()) {
          displayError("New name cannot be empty.");
          return;
        }
  
        try {
          const response = await axios.post(
            `${import.meta.env.VITE_BACKEND_URL}api/rename_item`,
            {
              path: props.currentPath,
              oldName: itemToRename.value.title,
              newName: newName.value,
            }
          );
          if (response.data.success) {
            emit('itemRenamed');
            closeDialog();
          } else {
            displayError(response.data.message || "Failed to rename item. Please try again.");
          }
        } catch (error) {
          displayError("Error connecting to the server. Please try again.");
          console.error("Error renaming item:", error);
        }
      };
  
      return {
        dialogVisible,
        newName,
        openDialog,
        closeDialog,
        renameItem,
        errorMessage,
        showError,
      };
    },
  });
  </script>