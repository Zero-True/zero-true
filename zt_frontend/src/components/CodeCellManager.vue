<template>
  <v-container>
    <add-cell 
      v-if="$devMode && !isAppRoute" 
      @createCodeCell="e => createCodeCell('', e)" 
    />
  </v-container>
  <v-container v-for="codeCell in notebook.cells">
    <component
      v-if="codeCell.cellType === 'code'"
      :is="getComponent(codeCell.cellType)"
      :cellData="codeCell"
      :completions="completions[codeCell.id]"
      @runCode="runCode"
      @saveCell="saveCell"
      @componentValueChange="componentValueChange"
      @deleteCell="deleteCell"
      @createCell="createCodeCell"
      @copilotCompletion="copilotCompletion"
    />
    <component
      v-else
      :is="getComponent(codeCell.cellType)"
      :cellData="codeCell"
      @runCode="runCode"
      @saveCell="saveCell"
      @componentValueChange="componentValueChange"
      @deleteCell="deleteCell"
      @createCell="createCodeCell"
    />
  </v-container>
</template>

<script lang="ts">
import { Notebook, CodeCell } from "@/types/notebook";
import CodeComponent from "@/components/CodeComponent.vue";
import MarkdownComponent from "@/components/MarkdownComponent.vue";
import EditorComponent from "@/components/EditorComponent.vue";
import SQLComponent from "@/components/SQLComponent.vue";
import PackageComponent from "@/components/PackageComponent.vue";
import AddCell from '@/components/AddCell.vue'
import { PropType } from "vue";
import { useRoute } from "vue-router";
import { callbackify } from "util";


export default {
  props: {
    notebook: {
      type: Object as PropType<Notebook>,
      required: true,
    },
    completions: {
      type: Object as PropType<{ [key: string]: string[] }>,
      required: true,
    },
  },
  inheritAttrs: false,
  emits: ['runCode', 'deleteCell', 'saveCell', 'createCell', 'componentValueChange', 'copilotCompletion'],

  components: {
    "add-cell": AddCell,
    CodeComponent,
    MarkdownComponent,
    EditorComponent,
    SQLComponent,
    PackageComponent,
  },

  data() {
    return {
      menu_items: [
        { title: "Code" },
        { title: "SQL" },
        { title: "Markdown" },
        { title: "Text" },
      ],
      concatenatedCodeCache: {
        lastCellId: "" as string,
        code: "" as string,
        length: 0 as number,
      },
    };
  },
  computed: {
    isAppRoute() {
      const route = useRoute()
      return route.path === '/app'
    },
  },
  
  methods: {
    getComponent(cellType: string) {
      switch (cellType) {
        case "code":
          return "CodeComponent";
        case "text":
          return "EditorComponent";
        case "markdown":
          return "MarkdownComponent";
        case "sql":
          return "SQLComponent";
        default:
          throw new Error(`Unknown component type: ${cellType}`);
      }
    },

    runCode(cellId: string, componentId: string, code: string) {
      this.$emit("runCode", cellId, componentId);
    },
    deleteCell(cellId: string) {
      this.$emit("deleteCell", cellId);
    },
    saveCell(cellId: string, text: string, line: string, column: string) {
      this.$emit("saveCell", cellId, text, line, column);
    },
    createCodeCell(position_key: string, cellType: string) {
      this.$emit("createCell", position_key, cellType);
    },
    componentValueChange(cell: CodeCell, componentId: string, componentValue: any) {
      this.$emit("componentValueChange", cell, componentId, componentValue);
    },
    copilotCompletion(cellId: string, line: string, column: string, callback: any) {
      this.$emit("copilotCompletion", cellId, line, column, callback);
    },
  },
};
</script>

<style>
.cm-editor {
  height: auto !important;
}
</style>
