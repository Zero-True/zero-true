<template>
  <v-container style="margin-top: 12px;">
    <add-cell 
      v-if="$devMode && !isAppRoute" 
      @createCodeCell="e => createCodeCell('', e)" 
    />
  </v-container>
  <v-container
    :class="[
      'cell-container',
      { 'cell-container--app':  !$devMode || isAppRoute },
      { 'cell-container--wide': notebook.wideMode }
    ]"
    v-for="codeCell in notebook.cells"
  >
    <component
      v-if="codeCell.cellType === 'code'"
      :is="getComponent(codeCell.cellType)"
      :cellData="codeCell"
      :completions="completions[codeCell.id]"
      :lintResults="lintResults[codeCell.id] || []"
      :currentlyExecutingCell="currentlyExecutingCell"
      :isCodeRunning="isCodeRunning"
      @runCode="runCode"
      @saveCell="saveCell"
      @componentValueChange="componentValueChange"
      @deleteCell="deleteCell"
      @createCell="createCodeCell"
      @copilotCompletion="copilotCompletion"
      @updateTimers="updateTimers"
      @navigateToCell="handleCellNavigation"
      :ref="'cellComponent' + codeCell.id"
    />
    <component
      v-else
      :is="getComponent(codeCell.cellType)"
      :cellData="codeCell"
      :currentlyExecutingCell="currentlyExecutingCell"
      :isCodeRunning="isCodeRunning"
      @runCode="runCode"
      @saveCell="saveCell"
      @componentValueChange="componentValueChange"
      @deleteCell="deleteCell"
      @createCell="createCodeCell"
      @navigateToCell="handleCellNavigation"
      :ref="'cellComponent' + codeCell.id"
    />
  </v-container>
</template>

<script lang="ts">
import { Notebook, CodeCell } from "@/types/notebook";
import CodeComponent from "@/components/cells/code/CodeComponent.vue";
import MarkdownComponent from "@/components/cells/markdown/MarkdownComponent.vue";
import EditorComponent from "@/components/cells/text/EditorComponent.vue";
import SQLComponent from "@/components/cells/sql/SQLComponent.vue";
import PackageComponent from "@/components/plugins/PackageComponent.vue";
import AddCell from '@/components/cells/base/AddCell.vue'
import { PropType } from "vue";
import { useRoute } from "vue-router";


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
    lintResults: {
      type: Object as PropType<{ [key: string]: string[] }>,
      required: true,
    },
     currentlyExecutingCell: {
      type: String,
      default: null
    },
    isCodeRunning:{
      type: Boolean,
      default: false
    },
  },
  inheritAttrs: false,
  emits: ['runCode', 'deleteCell', 'saveCell', 'createCell', 'componentValueChange', 'copilotCompletion', 'updateTimers'],

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

    runCode(cellId: string, nonReactive: boolean, componentId: string) {
      this.$emit("runCode", cellId, nonReactive, componentId);
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
    componentValueChange(cell: CodeCell, componentId: string, componentValue: any, nonReactive: boolean) {
      this.$emit("componentValueChange", cell, componentId, componentValue, nonReactive);
    },
    copilotCompletion(cellId: string, line: string, column: string, callback: any) {
      this.$emit("copilotCompletion", cellId, line, column, callback);
    },
    updateTimers(cellId: string, value: boolean) {
      this.$emit("updateTimers", cellId, value);
    }, 
    scrollToCellView(cellId: string): void {
  try {
    const cell = document.getElementById(`codeCard${cellId}`);
    if (!cell) {
      return;
    }

    const viewport = {
      top: window.scrollY,
      bottom: window.scrollY + window.innerHeight
    };

    const cellPosition = {
      top: cell.getBoundingClientRect().top + viewport.top,
      bottom: cell.getBoundingClientRect().bottom + viewport.top
    };

    const isOutsideViewport = 
      cellPosition.top < viewport.top || 
      cellPosition.bottom > viewport.bottom;

    if (isOutsideViewport) {
      cell.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      });
    }
  } catch (error) {
    console.error('Failed to scroll to cell:', error);
  }
},
    handleCellNavigation(currentCellId: string, direction: 'up' | 'down') {
    const cellIds = Object.keys(this.notebook.cells);
    const currentIndex = cellIds.indexOf(currentCellId);

    if (currentIndex === -1) {
      return;
    }

    const targetIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;

    if (targetIndex < 0 || targetIndex >= cellIds.length) {
      // No cell to navigate to in the given direction
      return;
    }

    const targetCellId = cellIds[targetIndex];
    const targetCell = this.notebook.cells[targetCellId];

     //scroll to the target cell
     this.scrollToCellView(targetCellId);
    this.$nextTick(async () => {
      const cellComponentRef = this.$refs['cellComponent' + targetCellId];

      if (!cellComponentRef) {
        return;
      }

      const cellComponent = Array.isArray(cellComponentRef)
        ? cellComponentRef[0]
        : cellComponentRef;

      if (!cellComponent || typeof cellComponent.getEditorView !== 'function') {
        return;
      }

      try {
        const view = await cellComponent.getEditorView();
        if (view) {
          if (view.focus) {
            view.focus();
          }
          if (targetCell.cellType === 'text') {
            const contentLength = view.getContent({ format: 'text' }).length;
            const pos = direction === 'up' ? contentLength : 0;
            const body = view.getBody();
            const lastNode = body.lastChild;
            if (lastNode) {
              const range = document.createRange();
              view.selection.setRng(range);
            }
          } 
          else {
            // Handle CodeMirror editor
            const pos = direction === 'up' ? view.state.doc.length : 0;
            if (view.dispatch) {
              view.dispatch({
                selection: { anchor: pos },
              });
            }
          }
        }
      } catch (error) {
        console.error('Error accessing editor view:', error);
      }
    });
  },
  },
};
</script>

<style lang="scss">
.cell-container {
  width: 100%;
  padding-top: 0;
  &--app {
    padding-bottom: 0;
  }
  &--wide {
    max-width: 100% !important;
    margin: 0% !important;
  }
}
.cm-editor {
  height: auto !important;
}
</style>
