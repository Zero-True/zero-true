<template>
  <v-dialog
    v-model="uploadingFile"
    width="444"
    class="text-center mb-8"
    rounded="lg"
  >
    <template v-slot:activator="{ props }">
      <v-btn
        v-bind="props"
        class="mb-2"
        icon="mdi-upload"
        color="bluegrey-darken-4"
      >
      </v-btn>
    </template>
    <v-card @drop="onDrop" @dragover.prevent>
      <input
        class="d-none"
        type="file"
        ref="fileInput"
        @change="handleFileChange"
      />
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
      <v-btn @click="submitFile" color="primary" class="mt-4">Submit</v-btn>
      <v-snackbar v-model="snackbar" :timeout="3000" top>
        {{ snackbarText }}
      </v-snackbar>
    </v-card>
  </v-dialog>
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
      this.file = file;
      this.fileName = file.name;
    },
    async submitFile() {
      if (this.file) {
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
          this.uploadingFile = false;
          this.$emit("file-uploaded");
        } catch (error) {
          console.error("Error processing file:", error);
          this.snackbarText = "Error uploading file";
          this.snackbar = true;
        }
      } else {
        console.error("No file to submit");
        this.snackbarText = "No file selected";
        this.snackbar = true;
      }
    },
    cleanUp() {
      this.file = null;
      this.fileName = "";
      this.snackbarText = "";
    },
  },
};
</script>

<style scoped>
/* Add any required styling here */
</style>
