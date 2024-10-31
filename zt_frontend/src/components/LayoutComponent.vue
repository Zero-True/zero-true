<template>
  <v-row v-if="rowData">
    <v-col
      v-for="(component, componentIndex) in rowData.components"
      :key="componentIndex"
      :cols="componentWidth(component)"
    >
      <div v-if="typeof component === 'string'">
        <component-wrapper 
            :renderComponents="[components[component]]" 
            :allComponents="components"
            @runCode="runCode"/>
      </div>
      <div v-else>
        <layout-component
          :column-data="component"
          :components="components"
          @runCode="runCode"
        />
      </div>
    </v-col>
  </v-row>
  <div v-if="columnData">
    <div
      v-for="(component, componentIndex) in columnData.components"
      :key="componentIndex"
    >
      <div v-if="typeof component === 'string'">
        <component-wrapper 
            :renderComponents="[components[component]]" 
            :allComponents="components"
            @runCode="runCode"/>
      </div>
      <div v-else>
        <layout-component
          :row-data="component"
          :components="components"
          @runCode="runCode"
        />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import type { PropType } from "vue";
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
  VCard
} from "vuetify/lib/components/index.mjs";
import { VDataTable } from "vuetify/components/VDataTable";
import { Column, ZTComponent, Row } from "@/types/notebook";
import PlotlyPlot from "@/components/PlotlyComponent.vue";
import TextComponent from "@/components/TextComponent.vue"
import ComponentWrapper from "@/components/ComponentWrapper.vue";

export default {
  emits: ["runCode"],
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
    "v-text":TextComponent,
    "plotly-plot": PlotlyPlot,
    "component-wrapper": ComponentWrapper,
  },
  props: {
    rowData: {
      type: Object as PropType<Row>,
    },
    columnData: {
      type: Object as PropType<Column>,
    },
    components: {
      type: Object as PropType<Record<string, ZTComponent>>,
      required: true,
    },
  },
  methods: {
    runCode(fromComponent: boolean, componentId: string, componentValue: any) {
      this.$emit("runCode", fromComponent, componentId, componentValue);
    },
    componentWidth(component: any) {
      return component.width ? component.width : false;
    },
  },
};
</script>
