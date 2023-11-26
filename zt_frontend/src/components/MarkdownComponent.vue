<template>
  <v-card flat color="bluegrey">
    <v-row v-if="$devMode" no-gutters class="py-1 toolbar-bg">
      <v-col :cols="11">
        <span class="py-0 px-2">.md</span>

        <!-- Placeholder for future content or can be empty -->
      </v-col>
      <v-col :cols="1" class="d-flex justify-end align-center py-0">
        <v-icon small class="mx-1" color="primary" @click="saveCell">
          mdi-content-save
        </v-icon>
        <v-icon small class="mx-1" color="error" @click="deleteCell">
          mdi-delete
        </v-icon>
      </v-col>
    </v-row>
    <ace-editor
      v-if="$devMode"
      v-model:value="cellData.code"
      ref="editor"
      class="editor"
      theme="dracula"
      lang="markdown"
      @focus="handleFocus(true)"
      @blur="handleFocus(false)"
      :options="editorOptions"
    />
    <div v-if="$devMode">
      <p class="text-caption text-disabled text-right">
        CTRL+Enter to save</p>
    </div>
    <div v-html="compiledMarkdown"></div>
  </v-card>
</template>

<script lang="ts">
import type { PropType } from "vue";
import { marked } from 'marked';
import { VAceEditor } from "vue3-ace-editor";
import "ace-builds/src-noconflict/mode-markdown";
import "ace-builds/src-noconflict/snippets/markdown";
import "ace-builds/src-noconflict/ext-language_tools";
import "ace-builds/src-noconflict/theme-dracula";
import { CodeCell } from "@/types/notebook";

export default {
  components: {
    "ace-editor": VAceEditor,
  },
  computed: {
    editorOptions() {
      return {
        showPrintMargin: false,
        enableBasicAutocompletion: true,
        enableSnippets: true,
        enableLiveAutocompletion: true,
        autoScrollEditorIntoView: true,
        highlightActiveLine: this.isFocused,
        highlightGutterLine: this.isFocused,
        minlines: 1,
        maxLines: Infinity,
      };
    },
    compiledMarkdown() {
      return marked.parse(this.cellData.code);
    },
  },
  data() {
    return {
      isFocused: false, // add this line to keep track of the focus state
    };
  },
  props: {
    cellData: {
      type: Object as PropType<CodeCell>,
      required: true,
    },
  },
  mounted() {
    // Attach the event listener when the component is mounted
    if(this.$devMode){
      const aceComponent = this.$refs.editor as any;
      aceComponent._editor.renderer.$cursorLayer.element.style.display = "none";
    }
    window.addEventListener("keydown", this.handleKeyDown);
  },
  beforeUnmount() {
    // Remove the event listener before the component is destroyed
    window.removeEventListener("keydown", this.handleKeyDown);
  },
  methods: {
    handleKeyDown(event: KeyboardEvent) {
      if (this.isFocused && event.ctrlKey && event.key === "Enter") {
        this.saveCell();
      }
    },
    handleFocus(state: boolean) {
      if (state) {
        const aceComponent = this.$refs.editor as any;
        aceComponent._editor.renderer.$cursorLayer.element.style.display = "";
      } else {
        const aceComponent = this.$refs.editor as any;
        aceComponent._editor.renderer.$cursorLayer.element.style.display =
          "none";
      }
      this.isFocused = state;
    },
    saveCell() {
      this.$emit("saveCell", this.cellData.id);
    },
    deleteCell() {
      this.$emit("deleteCell", this.cellData.id);
    },
  },
};
</script>
