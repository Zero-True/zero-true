<template>
  <v-dialog
    v-model="uploadingFile"
    max-width="444"
    class="text-center mb-6"
    persistent
    @drop="onDrop"
    @dragover.prevent
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
    <v-alert v-if="errorMessage" color="error" :text="errorMessage"/>
    <v-card
      ><v-card-title class="pb-0" style="font-size: 18px"
        >Drag files to upload
        <div class="mb-1" style="font-size: 14px">or</div>
      </v-card-title>

      <v-card-text>
        <v-btn
          icon
          @click="closeDialog"
          v-if="!isUploading"
          class="close-button"
          variant="plain"
          style="width: 24px; height: 24px"
        >
          <v-icon size="18">mdi-close</v-icon>
        </v-btn>
        <input
          class="d-none"
          type="file"
          ref="fileInput"
          multiple
          @change="handleFileChange"
        />

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
        <div v-if="fileNames.length > 0" class="my-4">
          <span v-for="fileName in fileNames">{{ fileName }} <br /></span>
        </div>
      </v-card-text>
      <v-btn
        @click="submitFile"
        color="primary"
        class="mt-4"
        :disabled="isUploading"
      >
        <span v-if="!isUploading">Submit</span>
        <v-progress-circular
          v-if="isUploading"
          indeterminate
          color="primary"
          size="24"
        />
      </v-btn>
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
    files: [] as Array<File>,
    fileNames: [] as Array<string>,
    isUploading: false,
    ztAliases,
    errorMessage: "",
  }),
  methods: {
    openDialog() {
      this.uploadingFile = true;
    },
    closeDialog() {
      if (!this.isUploading) {
        this.uploadingFile = false;
      }
      this.cleanUp();
    },
    onDrop(event: DragEvent) {
      event.preventDefault();
      const files = event.dataTransfer?.files;
      if (files && files.length > 0) {
        for (let i = 0; i < files.length; i++) {
          this.files.push(files[i]);
          this.fileNames.push(files[i].name);
        }
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
      const files = (event.target as HTMLInputElement).files;
      if (files && files.length > 0) {
        for (let i = 0; i < files.length; i++) {
          this.files.push(files[i]);
          this.fileNames.push(files[i].name);
        }
      } else {
        console.error("No file selected");
      }
    },
    async submitFile() {
      for (const file of this.files) {
        this.isUploading = true;
        try {
          const chunkSize = 1024 * 512;
          const totalChunks = Math.ceil(file.size / chunkSize);
          for (let i = 0; i < totalChunks; i++) {
            const start = i * chunkSize;
            const end = Math.min(file.size, start + chunkSize);
            const chunk = file.slice(start, end);
            const formData = new FormData();
            formData.append("file", chunk);
            formData.append("chunk_index", String(i));
            formData.append("total_chunks", String(totalChunks));
            formData.append("path", this.currentPath);
            formData.append("file_name", file.name);
            await axios.post(
              import.meta.env.VITE_BACKEND_URL + "api/upload_file",
              formData,
              {
                headers: { "Content-Type": "multipart/form-data" },
              }
            );
          }
        } catch (error) {
          console.error("Error processing file:", error);
          this.errorMessage = "Error uploading file";
          this.isUploading = false;
        }
      }
      this.$emit("file-uploaded");

      this.isUploading = false;
      this.closeDialog();
    },

    cleanUp() {
      this.files = [];
      this.fileNames = [];
      this.errorMessage = "";
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
