<template>
  <code-cell-manager
    :notebook="notebook"
    :completions="completions"
    :lintResults="lintResults"
    :runCode="runCode"
    :saveCell="saveCell"
    :componentValueChange="componentValueChange"
    :deleteCell="deleteCell"
    :createCell="createCodeCell"
  >
  </code-cell-manager>
</template>

<script lang="ts">
import CodeCellManager from "@/components/CodeCellManager.vue";
import { Notebook, CodeCell } from "@/types/notebook";
import { PropType } from "vue";

export default {
  metaInfo() {
    return {
      meta: {
        dev: true,
      },
    };
  },
  props: {
    notebook: {
      type: Object as PropType<Notebook>,
      required: true,
    },
    completions: {
      type: Object as PropType<{ [key: string]: string[] }>,
      required: true,
    },
    lintResults: {
      type: Object as PropType<{ [key: string]: string[] }>,
      required: true,
    },
    runCode: {
      type: Function,
      required: true,
    },
    saveCell: {
      type: Function,
      required: true,
    },
    componentValueChange: {
      type: Function,
      required: true,
    },
    deleteCell: {
      type: Function,
      required: true,
    },
    createCodeCell: {
      type: Function,
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

    
  },
};
</script>