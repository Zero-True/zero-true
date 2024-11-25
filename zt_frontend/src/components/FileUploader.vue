<template>
  <v-dialog
    v-model="uploadingDialog"
    max-width="500"
    persistent
    @drop.prevent="onDrop"
    @dragover.prevent
    @dragenter.prevent
  >
    <template v-slot:activator="{ props }">
      <v-btn
        v-bind="props"
        icon="mdi-upload"
        color="bluegrey-darken-4"
        class="mb-2"
        @click="openDialog"
      >
      </v-btn>
    </template>

    <v-card class="upload-dialog">
        <!-- Success overlay dialog -->
        <v-dialog v-model="showSuccessMessage" persistent max-width="300">
        <v-card>
          <v-card-text class="text-center pa-4">
            <v-icon color="success" size="48" class="mb-2">mdi-check-circle</v-icon>
            <div class="text-h6 mb-2">Upload Complete!</div>
            <div class="text-body-2">
              {{ uploadItems.length }} {{ uploadItems.length === 1 ? 'item' : 'items' }} uploaded successfully
            </div>
          </v-card-text>
        </v-card>
      </v-dialog>

      <v-card-title class="text-center pt-4">
        <span class="text-h6">Upload Files or Folders</span>
        <v-btn
          icon
          @click="closeDialog"
          v-if="!isUploading"
          class="close-button"
          variant="plain"
        >
          <v-icon size="20">mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text class="text-center">
        <v-alert
          v-if="errorMessage"
          color="error"
          variant="tonal"
          closable
          class="mb-4"
          @click:close="errorMessage = ''"
        >
          {{ errorMessage }}
        </v-alert>

        <!-- Upload Area -->
        <div
          class="upload-area pa-6 mb-4"
          :class="{ 'drag-over': isDragging }"
          @dragenter="isDragging = true"
          @dragleave="isDragging = false"
          @drop="isDragging = false"
        >
          <v-icon size="48" color="primary" class="mb-2">mdi-cloud-upload</v-icon>
          <div class="text-body-1 mb-2">
            Drag and drop your files or folders here
          </div>
          <div class="text-body-2 text-medium-emphasis mb-4">or</div>
          
          <div class="d-flex justify-center gap-4">
            <!-- File Input -->
            <input
              ref="fileInput"
              type="file"
              multiple
              class="d-none"
              @change="handleFileChange"
            />
            <v-btn
              color="primary"
              variant="outlined"
              @click="triggerFileInput"
              :disabled="isUploading"
              prepend-icon="mdi-file-multiple"
              class="mr-2"
            >
              Choose Files
            </v-btn>

            <!-- Folder Input -->
            <input
              ref="folderInput"
              type="file"
              webkitdirectory
              directory
              multiple
              class="d-none"
              @change="handleFolderChange"
            />
            <v-btn
              color="primary"
              variant="outlined"
              @click="triggerFolderInput"
              :disabled="isUploading"
              prepend-icon="mdi-folder"
            >
              Choose Folder
            </v-btn>
          </div>
        </div>

        <!-- Selected Files List -->
        <div v-if="uploadItems.length > 0" class="selected-files">
          <div class="text-subtitle-1 mb-2">Selected Items:</div>
          <v-list density="compact" class="bg-grey-lighten-4 rounded">
            <v-list-item
              v-for="(item, index) in uploadItems"
              :key="index"
              :title="item.name"
              :subtitle="formatFileSize(item.size)"
            >
              <template v-slot:prepend>
                <v-icon :icon="item.isFolder ? 'mdi-folder' : 'mdi-file'" />
              </template>
              <template v-slot:append>
                <v-btn
                  icon="mdi-close"
                  variant="plain"
                  density="compact"
                  @click="removeItem(index)"
                  v-if="!isUploading"
                >
                </v-btn>
              </template>
            </v-list-item>
          </v-list>
        </div>
      </v-card-text>

  
      <v-card-actions class="pa-3 bg-dark">
        <v-spacer />
        <v-btn
          color="grey"
          variant="text"
          @click="closeDialog"
          :disabled="isUploading"
          class="mr-2"
        >
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          :loading="isUploading"
          :disabled="uploadItems.length === 0 || isUploading"
          @click="submitFiles"
          class="px-6"

        >
        {{ isUploading ? 'Uploading...' : 'Upload' }}
        </v-btn>
       
      </v-card-actions>

      <!-- Upload Progress -->
      <div v-if="isUploading" class="pa-4 pt-0">
        <v-progress-linear
          v-model="uploadProgress"
          color="primary"
          height="20"
          rounded
        >
          <template v-slot:default="{ value }">
            <span class="white--text">{{ Math.ceil(value) }}%</span>
          </template>
        </v-progress-linear>
      </div>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import axios from 'axios';

interface UploadItem {
  file: File;
  name: string;
  size: number;
  relativePath: string;
  isFolder: boolean;
}

export default defineComponent({
  name: 'FileUploader',
  props: {
    currentPath: {
      type: String,
      required: true,
    },
  },
  emits: ['file-uploaded'],
  
  data() {
    return {
      uploadingDialog: false,
      isDragging: false,
      isUploading: false,
      errorMessage: '',
      uploadItems: [] as UploadItem[],
      uploadProgress: 0,
      showSuccessMessage: false,

    };
  },

  methods: {

    triggerFileInput() {
    (this.$refs.fileInput as HTMLInputElement).click();
  },
  triggerFolderInput() {
    (this.$refs.folderInput as HTMLInputElement).click();
  },

    openDialog() {
      this.uploadingDialog = true;
    },

    closeDialog() {
      if (!this.isUploading) {
        this.uploadingDialog = false;
        this.cleanUp();
      }
    },

    formatFileSize(bytes: number): string {
      if (bytes === 0) return '0 B';
      const k = 1024;
      const sizes = ['B', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
    },

    async handleFileChange(event: Event) {
      const input = event.target as HTMLInputElement;
      if (input.files) {
        this.processFiles(Array.from(input.files));
      }
    },

    async handleFolderChange(event: Event) {
      const input = event.target as HTMLInputElement;
      if (input.files) {
        this.processFiles(Array.from(input.files), true);
      }
    },

    processFiles(files: File[], isFolder = false) {
      for (const file of files) {
        const relativePath = (file as any).webkitRelativePath || file.name;
        this.uploadItems.push({
          file,
          name: relativePath,
          size: file.size,
          relativePath,
          isFolder,
        });
      }
    },

    removeItem(index: number) {
      this.uploadItems.splice(index, 1);
    },

    onDrop(event: DragEvent) {
      this.isDragging = false;
      const items = event.dataTransfer?.items;
      
      if (!items) return;

      const promises: Promise<void>[] = [];

      // Convert DataTransferItemList to Array for iteration
      Array.from(items).forEach(item => {
        if (item.kind === 'file') {
          const entry = item.webkitGetAsEntry();
          if (entry) {
            promises.push(this.processEntry(entry));
          }
        }
      });
      Promise.all(promises).then(() => {
        // All files processed
      });
    },

    async processEntry(entry: FileSystemEntry): Promise<void> {
      if (entry.isFile) {
        const fileEntry = entry as FileSystemFileEntry;
        const file = await this.getFileFromEntry(fileEntry);
        this.processFiles([file]);
      } else if (entry.isDirectory) {
        const dirEntry = entry as FileSystemDirectoryEntry;
        const reader = dirEntry.createReader();
        await this.readDirectory(reader, entry.fullPath);
      }
    },

    async readDirectory(reader: FileSystemDirectoryReader, path: string): Promise<void> {
      return new Promise((resolve) => {
        reader.readEntries(async (entries: FileSystemEntry[]) => {
          for (const entry of entries) {
            await this.processEntry(entry);
          }
          resolve();
        });
      });
    },

    getFileFromEntry(entry: FileSystemFileEntry): Promise<File> {
      return new Promise((resolve) => {
        entry.file((file: File) => {
          resolve(file);
        });
      });
    },

    async submitFiles() {
  if (this.isUploading) return; // Prevent multiple submissions
  
  this.isUploading = true;
  this.uploadProgress = 0;
  this.errorMessage = '';
  const totalSize = this.uploadItems.reduce((acc, item) => acc + item.size, 0);
  let uploadedSize = 0;

  try {
    // Process items sequentially to maintain order
    for (const item of this.uploadItems) {
      const file = item.file;
      const relativePath = item.relativePath;
      const chunkSize = 1024 * 512;
      const totalChunks = Math.ceil(file.size / chunkSize);
      
      // Upload chunks in sequence to maintain order
      for (let i = 0; i < totalChunks; i++) {
        const start = i * chunkSize;
        const end = Math.min(file.size, start + chunkSize);
        const chunk = file.slice(start, end);
        
        const formData = new FormData();
        formData.append('file', chunk);
        formData.append('chunk_index', String(i));
        formData.append('total_chunks', String(totalChunks));
        formData.append('path', this.currentPath);
        formData.append('file_name', relativePath);
        formData.append('is_folder', String(item.isFolder));

        try {
          // Wait for each chunk to complete before sending the next
          await axios.post(
            `${import.meta.env.VITE_BACKEND_URL}api/upload_file`,
            formData,
            {
              headers: { 'Content-Type': 'multipart/form-data' },
            }
          );

          uploadedSize += chunk.size;
          this.uploadProgress = (uploadedSize / totalSize) * 100;
        } catch (error: any) {
        // Set the error message based on the type of error
        if (error.response) {
          switch (error.response.status) {
            case 409:
              this.errorMessage = `${item.isFolder ? 'Folder' : 'File'} "${relativePath}" already exists.`;
              return;
            case 503:
              this.errorMessage = 'Server is busy. Please try again later.';
              return;
            case 413:
              this.errorMessage = 'File is too large to upload.';
              return;
            case 400:
              this.errorMessage = 'Invalid file or upload parameters.';
              return;
            case 500:
              this.errorMessage = 'Server error occurred. Please try again later.';
              return;
            default:
              this.errorMessage = `Upload failed: ${error.response.data.detail || 'Unknown error'}`;
              return;
          }
        } else if (error.request) {
          this.errorMessage = 'Network error. Please check your connection.';
          return;
        } else {
          this.errorMessage = 'Upload failed. Please try again.';
          return;
        }
      }

      }
    }

    // Show success message
    this.showSuccessMessage = true;
    this.$emit('file-uploaded');

    // Close success message and dialog after delay
    setTimeout(() => {
      this.showSuccessMessage = false;
      this.closeDialog();
    }, 500);
    
  } catch (error) {
    console.error('Upload error:', error);
    // Error message is already set in the inner try-catch
  } finally {
    this.isUploading = false;
  }
},
    
    cleanUp() {
      this.uploadItems = [];
      this.errorMessage = '';
      this.uploadProgress = 0;
      this.isDragging = false;
    },
  },
});
</script>

<style scoped>
.upload-dialog {
  position: relative;
}

.close-button {
  position: absolute;
  top: 8px;
  right: 8px;
}

.upload-area {
  border: 2px dashed var(--v-primary-base);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.upload-area.drag-over {
  background-color: rgba(var(--v-primary-base), 0.1);
  border-color: var(--v-primary-darken-1);
}

.selected-files {
  max-height: 200px;
  overflow-y: auto;
}
</style>