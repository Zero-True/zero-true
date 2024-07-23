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
    formData: null as FormData | null,
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
      this.formData = new FormData();
      this.formData.append("file", file);
      this.fileName = file.name;
      console.log(file); // process the file
    },
    async submitFile() {
      if (this.formData) {
        try {
          this.formData.append("path", this.currentPath);
          const response = await axios.post(
            import.meta.env.VITE_BACKEND_URL + "api/upload_file",
            this.formData,
            {
              headers: { "Content-Type": "multipart/form-data" },
            }
          );
          console.log("File processed", response.data);
          this.snackbarText = "File uploaded successfully";
          this.snackbar = true;
          this.uploadingFile = false; // Close the dialog
          this.$emit("file-uploaded"); // Emit event to refresh file list
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
      this.formData = null;
      this.fileName = "";
      this.snackbarText = "";
    },
  },
};
</script>

<style scoped>
/* Add any required styling here */
</style>
