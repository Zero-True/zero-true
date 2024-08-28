<template>
    <div>
      <v-dialog v-model="dialogVisible" max-width="500px">
        <v-card>
          <v-card-title>Confirm Deletion</v-card-title>
          <v-card-text>
            Are you sure you want to delete "{{ itemToDelete?.title }}"?
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn color="blue-darken-1" @click="closeDialog">Cancel</v-btn>
            <v-btn color="error" @click="deleteItem">Delete</v-btn>
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
  import { defineComponent, ref } from 'vue';
  import axios from 'axios';
  
  export default defineComponent({
    name: 'DeleteItem',
    props: {
      currentPath: {
        type: String,
        required: true
      },
      isProtectedFile: {
        type: Function,
        required: true,
      },
    },
    emits: ['itemDeleted'],
    setup(props, { emit }) {
      const dialogVisible = ref(false);
      const itemToDelete = ref<any>(null);
      const errorMessage = ref('');
      const showError = ref(false);
  
      const openDialog = (item: any) => {
        if (!props.isProtectedFile(item.title)) {
          itemToDelete.value = item;
          dialogVisible.value = true;
        }
      };
  
      const closeDialog = () => {
        dialogVisible.value = false;
        itemToDelete.value = null;
      };
  
      const displayError = (message: string) => {
        errorMessage.value = message;
        showError.value = true;
      };
  
      const deleteItem = async () => {
        try {
          const response = await axios.post(
            `${import.meta.env.VITE_BACKEND_URL}api/delete_item`,
            {
              path: props.currentPath,
              name: itemToDelete.value.title,
            }
          );
          if (response.data.success) {
            emit('itemDeleted');
            closeDialog();
          } else {
            displayError(`Failed to delete item: ${response.data.message}`);
          }
        } catch (error) {
          displayError("Error connecting to the server. Please try again.");
          console.error('Error deleting item:', error);
        }
      };
  
      return {
        dialogVisible,
        itemToDelete,
        openDialog,
        closeDialog,
        deleteItem,
        errorMessage,
        showError,
      };
    }
  });
  </script>