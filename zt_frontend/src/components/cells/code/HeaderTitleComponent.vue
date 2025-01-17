<template>
    <div v-if="!devMode || isAppRoute || isMobile" style="display: flex; width: 100%">
      <h4 v-if="cellData.hideCode" class="text-bluegrey-darken-1 text-ellipsis app-static-name">
        {{ cellData.cellName }}
      </h4>
      <v-expansion-panels :model-value="expanded" @update:model-value="updateExpanded">
        <v-expansion-panel :model-value="expanded" bg-color="bluegrey-darken-3">
          <v-expansion-panel-title
            class="text-bluegrey-darken-1"
            :id="'codeMirrorAppTitle' + cellData.id"
          >
            <h4 class="text-ellipsis app-static-name">
              {{ cellData.cellName }}
            </h4>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <codemirror
              v-model="cellData.code"
              :style="{ height: '400px' }"
              :autofocus="true"
              :indent-with-tab="true"
              :tab-size="2"
              :viewportMargin="Infinity"
              :extensions="extensions"
              :code="cellData.code"
              :id="'codeMirrorApp' + cellData.id"
            />
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </div>
  </template>
  
  <script lang="ts">
  export default {
    props: {
      cellData: { type: Object, required: true },
      expanded: { type: Array, required: true }, // Accept expanded as a prop
      extensions: { type: Array, required: true },
      devMode: { type: Boolean, required: true },
      isAppRoute: { type: Boolean, required: true },
      isMobile: { type: Boolean, required: true },
    },
    emits: ["update:expanded"], // Emit update:expanded event
    methods: {
      updateExpanded(value:any) {
        this.$emit("update:expanded", value); // Emit event when expanded changes
      },
    },
  };
  </script>