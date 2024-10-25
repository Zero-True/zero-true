<template>
  <v-dialog
    v-model="uploadingFile"
    max-width="444"
    class="text-center mb-6"
    persistent
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
    <v-card @drop="onDrop" @dragover.prevent>
      <v-btn
        icon
        @click="closeDialog"
        v-if="!isUploading"
        class="close-button"
        variant="plain"
        style="width: 24px; height: 24px;"
      >
        <v-icon size="18">mdi-close</v-icon>
      </v-btn>
      <input
        class="d-none"
        type="file"
        ref="fileInput"
        @change="handleFileChange"
      />
      <v-card-title class="pb-0" style="font-size: 18px;">Drag files to upload</v-card-title>
      <div class="mb-1" style="font-size: 14px;">or</div>
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
      <v-btn @click="submitFile" color="primary" class="mt-4" :disabled="isUploading">
        <span v-if="!isUploading">Submit</span>
        <v-progress-circular v-if="isUploading" indeterminate color="primary" size="24" />
      </v-btn>
    </v-card>
  </v-dialog>
  <v-snackbar v-model="snackbar" :timeout="400" location="center">
        {{ snackbarText }}
      </v-snackbar>
</template>

<script lang="ts">
import axios from "axios";
import { ztAliases } from "@/iconsets/ztIcon";

export default {
  props: {
    currentPath: {
      type: String,
      required: true,
    },
  },
  emits: ["file-uploaded"],
  data: () => ({
    uploadingFile: false,
    fileInput: null,
    file: null as File | null,
    fileName: "",
    snackbar: false,
    snackbarText: "",
    isUploading: false,
    ztAliases,
  }),
  methods: {
    openDialog() {
      this.uploadingFile = true;
    },
    closeDialog() {
      if (!this.isUploading) {
        this.uploadingFile = false;
      }
    },
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
      this.file = file;
      this.fileName = file.name;
    },
    async submitFile() {
  if (this.file) {
    this.isUploading = true;
    try {
      const chunkSize = 1024 * 512;
      const totalChunks = Math.ceil(this.file.size / chunkSize);
      for (let i = 0; i < totalChunks; i++) {
        const start = i * chunkSize;
        const end = Math.min(this.file.size, start + chunkSize);
        const chunk = this.file.slice(start, end);
        const formData = new FormData();
        formData.append("file", chunk);
        formData.append("chunk_index", String(i));
        formData.append("total_chunks", String(totalChunks));
        formData.append("path", this.currentPath);
        formData.append("file_name", this.file.name);
        await axios.post(
          import.meta.env.VITE_BACKEND_URL + "api/upload_file",
          formData,
          {
            headers: { "Content-Type": "multipart/form-data" },
          }
        );
      }
      this.snackbarText = "File uploaded successfully";
      this.snackbar = true;
      this.$emit("file-uploaded");

       this.isUploading = false;
          this.closeDialog();
          this.cleanUp();

    } catch (error) {
      console.error("Error processing file:", error);
      this.snackbarText = "Error uploading file";
      this.snackbar = true;
      this.isUploading = false;
    } 
  } else {
    console.error("No file to submit");
  }
},

cleanUp() {
  this.file = null;
  this.fileName = "";
},

  },
};
</script>

<style scoped>
.close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 24px; 
  height: 24px;
}
</style>
