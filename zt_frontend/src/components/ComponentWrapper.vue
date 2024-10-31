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
        @update:model-value="
          (newValue: any) => {
            const files = Array.isArray(newValue)
              ? newValue
              : [newValue].filter(Boolean);
            uploadFiles(files);
          }
        "
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

    async uploadFile(file: File) {
      if (file) {
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
            formData.append("path", ".");
            formData.append("file_name", file.name);
            await axios.post(
              import.meta.env.VITE_BACKEND_URL + "api/upload_file",
              formData
            );
          }
        } catch (error) {
          console.error("Error processing file:", error);
        }
      } else {
        console.error("No file to submit");
      }
    },

    async uploadFiles(files: Array<File>) {
      for (const file of files) {
        await this.uploadFile(file);
      }
    },
  },
};
</script>
