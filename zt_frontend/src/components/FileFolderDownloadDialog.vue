<template>
  <div>
    <v-dialog v-model="dialogVisible" max-width="500px" persistent>
      <v-card>
        <v-card-title>Confirm Download</v-card-title>
        <v-card-text>
          Do you want to download "{{ itemToDownload?.title }}"{{ itemToDownload?.file === 'folder' ? ' as a ZIP file' : '' }}?
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="blue-darken-1" @click="closeDialog">Cancel</v-btn>
          <v-btn 
            color="primary" 
            @click="downloadItem"
            :loading="isDownloading"
          >
            Download
          </v-btn>
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
  name: 'DownloadItem',
  props: {
    currentPath: {
      type: String,
      required: true
    },
  },
  emits: ['itemDownloaded'],
  setup(props, { emit }) {
    const dialogVisible = ref(false);
    const itemToDownload = ref<any>(null);
    const errorMessage = ref('');
    const showError = ref(false);
    const isDownloading = ref(false);

    const openDialog = (item: any) => {
      itemToDownload.value = item;
      dialogVisible.value = true;
    };

    const closeDialog = () => {
      dialogVisible.value = false;
      itemToDownload.value = null;
      isDownloading.value = false;
    };

    const displayError = (message: string) => {
      errorMessage.value = message;
      showError.value = true;
    };

    const downloadItem = async () => {
      if (!itemToDownload.value) return;
      
      isDownloading.value = true;

      try {
        const response = await axios({
          url: `${import.meta.env.VITE_BACKEND_URL}api/download`,
          method: 'GET',
          params: {
            path: `${props.currentPath}/${itemToDownload.value.title}`,
            filename: itemToDownload.value.title,
            isFolder: itemToDownload.value.file === 'folder'
          },
          responseType: 'blob'
        });

        // Create blob link to download
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', itemToDownload.value.title + (itemToDownload.value.file === 'folder' ? '.zip' : ''));
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        emit('itemDownloaded');
        closeDialog();
      } catch (error) {
        console.error('Error downloading item:', error);
        displayError("Error downloading the item. Please try again.");
      } finally {
        isDownloading.value = false;
      }
    };

    return {
      dialogVisible,
      itemToDownload,
      openDialog,
      closeDialog,
      downloadItem,
      errorMessage,
      showError,
      isDownloading,
    };
  }
});
</script>