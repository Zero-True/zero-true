<template>
  <div v-for="component in renderComponents" :key="component.id">
    <v-row class="pa-5">
      <plotly-plot
        v-if="component.component === 'plotly-plot'"
        :id="component.id"
        :figureJson="component.figure_json as string"
      />

      <v-container
        v-else-if="component.component === 'zt-html'"
        v-html="component.v_html"
      />
      <component
        v-else-if="component.component === 'v-file-input'"
        :is="component.component"
        v-bind="componentBind(component)"
        :model-value="selectedFiles[component.id]"
        @update:model-value="
          (newValue: any) => handleFileSelection(newValue, component.id, component.accept)"
        :error="!!uploadErrors[component.id]"
        :error-messages="uploadErrors[component.id]"
        :loading="uploadLoading[component.id]"
        :append-icon="selectedFiles[component.id] && !uploadLoading[component.id] ? 'mdi-upload' : ''"
        :messages="uploadSuccess[component.id] ? 'File uploaded successfully!' : uploadMessages[component.id]"
        class="file-input-component"
        @click:append="handleUpload(component.id)"
        :disabled="uploadLoading[component.id]"
        :readonly="uploadLoading[component.id]"


      />
      <component
        v-else
        :is="component.component"
        v-bind="componentBind(component)"
        v-model="component.value"
        v-on="getEventBindings(component)"
      >
        <template v-slot:default v-if="component.component !== 'v-data-table'">
          <div v-if="component.childComponents">
            <component-wrapper
              :renderComponents="getChildren(component.childComponents as string[])"
              :allComponents="allComponents"
              @runCode="runCode"
            />
          </div>
          <div v-else-if="component.component === 'v-btn'">
            {{ component.text }}
          </div>
        </template>
      </component>
    </v-row>
  </div>
</template>

<script lang="ts">
import type { PropType } from "vue";
import { Components2, ZTComponent } from "@/types/notebook";
import {
  VSlider,
  VRating,
  VTextField,
  VFileInput,
  VTextarea,
  VRangeSlider,
  VSelect,
  VCombobox,
  VBtn,
  VImg,
  VAutocomplete,
  VCard,
} from "vuetify/lib/components/index.mjs";
import { VDataTable } from "vuetify/components/VDataTable";
import TextComponent from "@/components/TextComponent.vue";
import PlotlyPlot from "@/components/PlotlyComponent.vue";
import axios from "axios";

export default {
  components: {
    "v-slider": VSlider,
    "v-rating": VRating,
    "v-text-field": VTextField,
    "v-file-input": VFileInput,
    "v-textarea": VTextarea,
    "v-range-slider": VRangeSlider,
    "v-select": VSelect,
    "v-combobox": VCombobox,
    "v-btn": VBtn,
    "v-img": VImg,
    "v-data-table": VDataTable,
    "v-autocomplete": VAutocomplete,
    "v-card": VCard,
    "v-text": TextComponent,
    "plotly-plot": PlotlyPlot,
  },
  data() {
  return {
    selectedFiles: {} as Record<string, any>,
    uploadErrors: {} as Record<string, string>,
    uploadMessages: {} as Record<string, string>,
    uploadLoading: {} as Record<string, boolean>,
    uploadSuccess: {} as Record<string, boolean>,
  }
},
  emits: ["runCode"],
  props: {
    renderComponents: {
      type: Object as PropType<Components2>,
      required: true,
    },
    allComponents: {
      type: Object as PropType<Record<string, ZTComponent>>,
      required: true,
    },
  },
  methods: {
    componentBind(component: any) {
      if (component.component && component.component === "v-autocomplete") {
        const { value, ...rest } = component;
        return this.convertUnderscoresToHyphens(rest);
      }
      return this.convertUnderscoresToHyphens(component);
    },

    convertUnderscoresToHyphens(obj: any) {
      return Object.entries(obj).reduce((newObj: any, [key, value]) => {
        const modifiedKey = key.replace(/_/g, "-");
        newObj[modifiedKey] = value;
        return newObj;
      }, {});
    },

    getEventBindings(component: any) {
      if (component.component === "v-card") {
        return {};
      }

      return {
        [component.triggerEvent]: () =>
          this.runCode(true, component.id, component.value),
        keydown: ($event: any) =>
          this.handleEnterPress(
            $event,
            component.id,
            component.component,
            component.value
          ),
      };
    },

    handleEnterPress(e: any, id: string, component_type: any, value: any) {
      // Run code when Enter is pressed in a text, number or text are field
      if (
        e.key === "Enter" &&
        !e.shiftKey &&
        (component_type === "v-text-field" ||
          component_type === "v-textarea" ||
          component_type === "v-number-input")
      ) {
        this.runCode(true, id, value);
      }
    },

    getChildren(childComponents: string[]) {
      return childComponents.map((id) => {
        return this.allComponents[id];
      });
    },

    runCode(fromComponent: boolean, componentId: string, componentValue: any) {
      if (this.allComponents[componentId].component === "v-btn") {
        componentValue = true;
        this.allComponents[componentId].value = true;
      }
      this.$emit("runCode", fromComponent, componentId, componentValue);
    },
    handleFileSelection(newValue: any, componentId: string, accept: string) {
      // Clear previous states
      this.uploadErrors[componentId] = '';
      this.uploadSuccess[componentId] = false;
      this.uploadMessages[componentId] = '';
      
      if (!newValue) {
        this.selectedFiles[componentId] = null;
        return;
      }

      const files = Array.isArray(newValue) ? newValue : [newValue];
      
      for (const file of files) {
        if (!this.validateFileType(file, accept)) {
          this.uploadErrors[componentId] = `Invalid file type. Accepted types: ${accept}`;
          this.selectedFiles[componentId] = null;
          return;
        }
      }

      this.selectedFiles[componentId] = newValue;
    },

    async handleUpload(componentId: string) {
      // Double check to prevent multiple uploads
      if (this.uploadLoading[componentId]) {
        return;
      }

      if (!this.selectedFiles[componentId]) {
        this.uploadErrors[componentId] = 'Please select a file to upload';
        return;
      }

      // Set loading state immediately
      this.uploadLoading[componentId] = true;
      this.uploadErrors[componentId] = '';
      this.uploadSuccess[componentId] = false;

      try {
        const files = Array.isArray(this.selectedFiles[componentId])
          ? this.selectedFiles[componentId]
          : [this.selectedFiles[componentId]].filter(Boolean);
        
        await this.uploadFiles(files, componentId);
        
        // Show success state
        this.uploadSuccess[componentId] = true;
        
        // Clear file input and success state after delay
        setTimeout(() => {
          this.selectedFiles[componentId] = null;
          this.uploadSuccess[componentId] = false;
        }, 300);
        
      } catch (error: any) {
        console.error('Upload error:', error);
        
        // Improved error handling
        if (error.response?.data?.message) {
          // Use the exact error message from the backend
          this.uploadErrors[componentId] = error.response.data.message;
        } else if (error.message) {
          // Use the error message from the Error object
          this.uploadErrors[componentId] = error.message;
        } else {
          // Fallback error message
          this.uploadErrors[componentId] = 'Upload failed. Please try again.';
        }
        
        this.uploadSuccess[componentId] = false;
      } finally {
        this.uploadLoading[componentId] = false;
      }
    },

    async uploadFile(file: File, componentId: string) {
      const chunkSize = 1024 * 512; // 512KB chunks
      const totalChunks = Math.ceil(file.size / chunkSize);
      
      try {
        for (let i = 0; i < totalChunks; i++) {
          const start = i * chunkSize;
          const end = Math.min(file.size, start + chunkSize);
          const chunk = file.slice(start, end);
          
          const formData = new FormData();
          formData.append("file", chunk);
          formData.append("chunk_index", String(i));
          formData.append("total_chunks", String(totalChunks));
          formData.append("path", ".");
          formData.append("file_name", file.name);
          
          const response = await axios.post(
            `${import.meta.env.VITE_BACKEND_URL}api/upload_file`,
            formData
          );

          if (response.data?.error) {
            throw new Error(response.data.error);
          }
        }
      } catch (error: any) {
        this.uploadErrors[componentId] = error.message;
      }
    },
    validateFileType(file: File, accept: string): boolean {
      if (!accept || accept === '*') return true;
      
      const acceptedTypes = accept.split(',').map(type => {
        type = type.trim().toLowerCase();
        return type.startsWith('.') 
          ? file.name.toLowerCase().endsWith(type)
          : file.type.toLowerCase().includes(type.replace('*', ''));
      });
      
      return acceptedTypes.some(isValid => isValid);
    },

    async uploadFiles(files: Array<File>, componentId: string) {
      for (const file of files) {
        await this.uploadFile(file, componentId);
      }
    },
    
  },
};
</script>


<style scoped>
.file-input-component {
  position: relative;
}

.file-input-component :deep(.v-input__append) {
  padding-inline-start: 0;
}
</style>