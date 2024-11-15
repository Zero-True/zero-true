<template>
  <!-- Download trigger button/link -->
  <v-list-item-title 
    @click="handleOpen"
    class="d-flex align-center cursor-pointer hover-bg pa-2 rounded"
  >
    <v-icon size="small" class="mr-2">mdi-download</v-icon>
    Download
  </v-list-item-title>

  <!-- Download Dialog -->
  <v-dialog
    v-model="dialog"
    max-width="450px"
    persistent
    @click:outside="handleClose"
    transition="dialog-bottom-transition"
  >
    <v-card class="download-dialog">
      <!-- Dark themed header -->
      <v-card-title class="d-flex justify-space-between align-center pa-4 bg-dark">
        <div class="d-flex align-center">
          <v-icon 
            size="small" 
            class="mr-2" 
            color="grey-lighten-2"
          >{{ file === 'folder' ? 'mdi-folder-outline' : 'mdi-file-document-outline' }}</v-icon>
          <span class="text-h6 text-grey-lighten-2">Download {{ file === 'folder' ? 'Folder' : 'File' }}</span>
        </div>
        <v-btn
          icon="mdi-close"
          variant="text"
          @click="handleClose"
          :disabled="isDownloading"
          class="ml-2"
          color="grey-lighten-2"
        />
      </v-card-title>

      <!-- Item details -->
      <v-card-subtitle class="pa-3 bg-dark border-subtle">
        <div class="text-grey-lighten-2">
          <span class="text-caption">Selected item:</span>
          <span class="text-body-2 ml-2">{{ title }}</span>
        </div>
      </v-card-subtitle>

      <v-card-text class="pa-4 bg-dark">
        <!-- Error Alert -->
        <v-alert
          v-if="errorMessage"
          color="error"
          variant="tonal"
          closable
          class="mb-4"
          @click:close="errorMessage = ''"
        >
          <div class="d-flex align-center">
            <v-icon size="small" class="mr-2">mdi-alert-circle</v-icon>
            {{ errorMessage }}
          </div>
        </v-alert>

        <!-- Download info card -->
        <v-sheet
          class="pa-4 rounded bg-grey-darken-4 border-subtle mb-4"
        >
          <div class="d-flex align-items-center mb-2">
            <v-icon
              :icon="file === 'folder' ? 'mdi-folder' : 'mdi-file'"
              size="32"
              color="primary"
              class="mr-3"
            />
            <div>
              <div class="text-grey-lighten-2 text-body-1">{{ title }}</div>
              <div class="text-caption text-grey">
                {{ file === 'folder' ? 'Will be downloaded as ZIP file' : 'Ready for download' }}
              </div>
            </div>
          </div>
        </v-sheet>

        <!-- Download Progress -->
        <div v-if="isDownloading">
          <v-progress-linear
            v-model="downloadProgress"
            color="primary"
            height="15"
            rounded
            class="mb-2"
          >
            <template v-slot:default="{ value }">
              <span class="text-caption">{{ Math.ceil(value) }}%</span>
            </template>
          </v-progress-linear>
          <div class="text-caption text-grey-lighten-2 text-center">
            Downloading... please wait
          </div>
        </div>
      </v-card-text>

      <!-- Dark themed action buttons -->
      <v-card-actions class="pa-4 bg-dark">
        <v-spacer />
        <v-btn
          color="grey"
          variant="text"
          @click="handleClose"
          :disabled="isDownloading"
          class="mr-2"
        >
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          @click="downloadItem"
          :loading="isDownloading"
          :disabled="isDownloading"
          class="px-6"
        >
          <v-icon left class="mr-2">mdi-download</v-icon>
          {{ isDownloading ? 'Downloading...' : 'Download' }}
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- Success overlay dialog -->
    <v-dialog v-model="showSuccessMessage" persistent max-width="300">
      <v-card class="bg-dark">
        <v-card-text class="text-center pa-4">
          <v-icon color="success" size="48" class="mb-2">mdi-check-circle</v-icon>
          <div class="text-h6 text-grey-lighten-2 mb-2">Download Complete!</div>
          <div class="text-body-2 text-grey">
            File downloaded successfully
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-dialog>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import axios from 'axios';

export default defineComponent({
  name: 'FileFolderDownloadDialog',
  props: {
    currentPath: {
      type: String,
      required: true
    },
    title: {
      type: String,
      required: true
    },
    file: {
      type: String,
      required: true
    }
  },
  emits: ['file-downloaded'],
  
  setup(props, { emit }) {
    const dialog = ref(false);
    const errorMessage = ref('');
    const isDownloading = ref(false);
    const downloadProgress = ref(0);
    const showSuccessMessage = ref(false);

    const handleOpen = () => {
      dialog.value = true;
      errorMessage.value = '';
      downloadProgress.value = 0;
    };

    const handleClose = () => {
      if (!isDownloading.value) {
        dialog.value = false;
        errorMessage.value = '';
        downloadProgress.value = 0;
      }
    };

    const handleDownloadError = (error: any) => {
      if (error.response) {
        switch (error.response.status) {
          case 404:
            errorMessage.value = 'File not found.';
            break;
          case 503:
            errorMessage.value = 'Server is busy. Please try again later.';
            break;
          case 413:
            errorMessage.value = 'File is too large to download.';
            break;
          case 500:
            errorMessage.value = 'Server error occurred. Please try again later.';
            break;
          default:
            errorMessage.value = `Download failed: ${error.response.data?.detail || 'Unknown error'}`;
        }
      } else if (error.request) {
        errorMessage.value = 'Network error. Please check your connection.';
      } else {
        errorMessage.value = 'Download failed. Please try again.';
      }
    };

    const downloadItem = async () => {
      isDownloading.value = true;
      downloadProgress.value = 0;
      errorMessage.value = '';

      try {
        const downloadPath = `${props.currentPath}/${props.title}`.replace(/\/+/g, '/');
        const response = await axios({
          url: `${import.meta.env.VITE_BACKEND_URL}api/download`,
          method: 'GET',
          params: {
            path: downloadPath,
            filename: props.title,
            isFolder: props.file === 'folder'
          },
          responseType: 'blob',
          onDownloadProgress: (progressEvent) => {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 0));
            downloadProgress.value = percentCompleted;
          }
        });

        // Create blob link to download
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute(
          'download',
          props.title + (props.file === 'folder' ? '.zip' : '')
        );
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        
        // Show success message
        showSuccessMessage.value = true;
        emit('file-downloaded');
        
        // Close after delay
        setTimeout(() => {
          showSuccessMessage.value = false;
          handleClose();
        }, 200);
      } catch (error) {
        console.error('Error downloading item:', error);
        handleDownloadError(error);
      } finally {
        isDownloading.value = false;
      }
    };

    return {
      dialog,
      handleOpen,
      handleClose,
      downloadItem,
      errorMessage,
      isDownloading,
      downloadProgress,
      showSuccessMessage,
    };
  }
});
</script>

<style scoped>
.download-dialog {
  background-color: #282c34 !important;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.bg-dark {
  background-color: #282c34 !important;
}

.border-subtle {
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.hover-bg:hover {
  background-color: rgba(var(--v-theme-primary), 0.1);
}

.cursor-pointer {
  cursor: pointer;
}

/* Dark theme overrides */
:deep(.v-card) {
  background-color: #282c34;
  color: #abb2bf;
}

:deep(.v-alert) {
  background-color: rgba(var(--v-theme-error), 0.1) !important;
  color: rgb(var(--v-theme-error)) !important;
}

:deep(.v-progress-linear) {
  background-color: rgba(var(--v-theme-primary), 0.1) !important;
}
</style>