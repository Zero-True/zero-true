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
        :error="errors[component.id]?.hasError || false"
        :error-messages="errors[component.id]?.message || ''"
        @update:model-value="(newValue: any)=> handleFileInput(component, newValue)"
        @click:clear="() => handleFileClear(component)"
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
  data() {
    return {
      errors: {} as Record<string, { hasError: boolean; message: string }>,
    };
  },
  methods: {
    componentBind(component: any) {
      if (
        component.component &&
        (component.component === "v-autocomplete" ||
          component.component === "v-file-input")
      ) {
        const { value, ...rest } = component;
        return this.convertUnderscoresToHyphens(rest);
      }
      return this.convertUnderscoresToHyphens(component);
    },

    convertUnderscoresToHyphens(obj: Record<string, any>): Record<string, any> {
      return Object.entries(obj).reduce(
        (acc, [key, value]) => ({
          ...acc,
          [key.replace(/_/g, "-")]: value,
        }),
        {}
      );
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

    async handleFileInput(
      component: ZTComponent,
      newValue: File | File[] | null
    ): Promise<void> {
      // If no files, exit early
      if (!newValue) {
        return;
      }
      const files = Array.isArray(newValue) ? newValue : [newValue];

      // Validate file size (50MB limit)
      const totalSize = files.reduce((sum, file) => sum + file.size, 0);
      if (totalSize > 50 * 1024 * 1024) {
        this.setError(component.id, "Total file size must not exceed 50 MB");
        return;
      }
      this.clearError(component.id);
      try {
        component.value = await this.processFiles(files);
        this.$emit("runCode", true, component.id, component.value);
      } catch (error) {
        console.error("Error processing files:", error);
        this.setError(component.id, "Error processing files");
      }
    },
    handleFileClear(component: ZTComponent): void {
      component.value = {};
      this.$emit("runCode", true, component.id, component.value);
    },
    async processFiles(files: File[]): Promise<Record<string, string>> {
      const fileList: Record<string, string> = {};

      for (const file of files) {
        if (file) {
          const base64Content = await this.fileToBase64(file);
          fileList[file.name] = base64Content;
        }
      }

      return fileList;
    },
    async fileToBase64(file: File): Promise<string> {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = () => {
          const result = reader.result as string;
          const base64 = result.split(",")[1];
          // Add padding if needed
          resolve(
            base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), "=")
          );
        };
        reader.onerror = () => reject(new Error("Failed to read file"));
        reader.readAsDataURL(file);
      });
    },
    setError(componentId: string, message: string): void {
      this.errors[componentId] = {
        hasError: true,
        message,
      };
    },
    clearError(componentId: string): void {
      if (this.errors[componentId]) {
        this.errors[componentId] = {
          hasError: false,
          message: "",
        };
      }
    },

    async createFormData(files: Array<File>) {
      const fileList: { [key: string]: any } = {};
      for (const file of files) {
        if (file) {
          const fileb64 = await this.fileToBase64(file);
          fileList[file.name] = fileb64;
        }
      }
      return fileList;
    },
  },
};
</script>
