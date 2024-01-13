<template>
  <code-cell-manager
    :notebook="notebook"
    :completions="completions"
    @runCode="runCode"
    @saveCell="saveCell"
    @componentValueChange="componentValueChange"
    @deleteCell="deleteCell"
    @createCell="createCodeCell"
  >
  </code-cell-manager>
</template>

<script lang="ts">
import CodeCellManager from "@/components/CodeCellManager.vue";
import { Notebook, CodeCell } from "@/types/notebook";
import { PropType } from "vue";



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

  components: {
    CodeCellManager,
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
    componentValueChange(
      cell: CodeCell,
      componentId: string,
      componentValue: any
    ) {
      this.$emit("componentChange", cell, componentId, componentValue);
    },
  },
};
</script>
