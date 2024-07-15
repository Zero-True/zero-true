<template>
    <v-dialog v-model="uploadingFile" width="444">
      <template v-slot:activator="{ props }">
        <v-btn v-bind="props" color="primary" class="mb-2">
          <v-icon left>mdi-upload</v-icon>
          Upload files
        </v-btn>
      </template>
      <v-card
        class="pb-16 pt-6 text-center mb-8"
        border="lg dotted"
        rounded="lg"
        @drop="onDrop"
        @dragover.prevent
      >
        <input class="d-none" type="file" ref="fileInput" @change="handleFileChange" />
        <v-card-title class="pb-0">Drag files to upload</v-card-title>
        <div class="mb-1">or</div>
        <v-btn
          class="mb-2"
          color="primary"
          variant="outlined"
          size="large"
          text="Browse files"
          rounded="pill"
          @click="onClickBrowseFiles"
        >
          Browse files
        </v-btn>
        <div v-if="fileName" class="my-4">
          <strong>File selected:</strong> {{ fileName }}
        </div>
        <div class="text-body-2 text-medium-emphasis">
          <div class="mb-4">
            Max file size:
            <strong>50MB</strong>
          </div>
          <div>
            Supported types:
            <strong>JPG, PNG, PDF, DOCX</strong>
          </div>
        </div>
      </v-card>
      <template #actions>
        <v-btn color="surface-alt" @click="uploadingFile = false">Save Changes</v-btn>
        <v-btn variant="text" @click="uploadingFile = false" class="mt-4">Close</v-btn>
      </template>
      <v-btn @click="submitFile" color="primary" class="mt-4">Submit</v-btn>
      <v-snackbar v-model="snackbar" :timeout="3000" top>
        {{ snackbarText }}
      </v-snackbar>
    </v-dialog>
  </template>
  
  <script lang="ts">
  import axios from 'axios';
  import { ztAliases } from '@/iconsets/ztIcon';
  
  export default {
    data: () => ({
      uploadingFile: false,
      fileInput: null,
      formData: null,
      fileName: '',
      snackbar: false,
      snackbarText: '',
      ztAliases,
    }),
    methods: {
      onDrop(event: DragEvent) {
        event.preventDefault();
        const files = event.dataTransfer?.files;
        if (files && files.length > 0) {
          this.handleFileUpload(files[0]);
        } else {
          console.error("No file dropped");
        }
      },
      onClickBrowseFiles() {
        if (this.$refs.fileInput) {
          (this.$refs.fileInput as HTMLInputElement).click();
        }
      },
      handleFileChange(event: Event) {
        const file = (event.target as HTMLInputElement).files;
        if (file && file.length > 0) {
          this.handleFileUpload(file[0]);
        } else {
          console.error("No file selected");
        }
      },
      handleFileUpload(file: File) {
        this.formData = new FormData();
        this.formData.append("file", file);
        this.fileName = file.name;
        console.log(file); // process the file
      },
      async submitFile() {
        if (this.formData) {
          try {
            const response = await axios.post(import.meta.env.VITE_BACKEND_URL + 'api/upload_file', this.formData, {
              headers: { 'Content-Type': 'multipart/form-data' }
            });
            console.log("File processed", response.data);
            this.snackbarText = "File uploaded successfully";
            this.snackbar = true;
            this.uploadingFile = false; // Close the dialog
          } catch (error) {
            console.error("Error processing file:", error.response);
            this.snackbarText = "Error uploading file";
            this.snackbar = true;
          }
        } else {
          console.error("No file to submit");
          this.snackbarText = "No file selected";
          this.snackbar = true;
        }
      }
    }
  }
  </script>
  
  <style scoped>
  /* Add any required styling here */
  </style>
  