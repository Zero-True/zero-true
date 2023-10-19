<template>
  <v-card flat color="bluegrey">
    <v-row v-if="$devMode" no-gutters class="py-1 toolbar-bg">
      <v-col :cols="11">
        <span class="py-0 px-2">.sql</span>

        <!-- Placeholder for future content or can be empty -->
      </v-col>
      <v-col :cols="1" class="d-flex justify-end align-center py-0">
        <v-icon small class="mx-1" color="primary" @click="runCode">
          mdi-play
        </v-icon>
        <v-icon small class="mx-1" color="error" @click="deleteCell">
          mdi-delete
        </v-icon>
      </v-col>
    </v-row>
    <v-text-field
      v-if="$devMode"
      v-model="cellData.variable_name"
      label="Enter SQL variable name"
      density="compact"
    />
    <ace-editor
      v-if="$devMode"
      v-model:value="cellData.code"
      ref="editor"
      class="editor"
      theme="dracula"
      lang="sql"
      @focus="handleFocus(true)"
      @blur="handleFocus(false)"
      :options="editorOptions"
    />
    <v-expansion-panels v-else>
      <v-expansion-panel>
        <v-expansion-panel-title color="bluegrey2">
          View Source Code
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <ace-editor
            v-model:value="cellData.code"
            class="editor"
            theme="dracula"
            lang="sql"
            :readonly="true"
            :options="editorOptions"
          />
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
    <div v-if="$devMode">
      <p class="text-caption text-disabled text-right">
        CTRL+Enter to run</p>
    </div>
    <v-container v-for="component in cellData.components" :key="component.id">
      <component
        :is="component.component"
        v-bind="component"
        v-model="component.value"
        @[component.triggerEvent]="runCode"
      />
    </v-container>
    <div class="text-p">{{ cellData.output }}</div>
  </v-card>
</template>

<script lang="ts">
import type { PropType } from "vue";
import { VAceEditor } from "vue3-ace-editor";
import { VDataTable } from "vuetify/labs/VDataTable";
import "ace-builds/src-noconflict/mode-sql";
import "ace-builds/src-noconflict/snippets/sql";
import "ace-builds/src-noconflict/ext-language_tools";
import "ace-builds/src-noconflict/theme-dracula";
import { CodeCell } from "@/types/notebook";

export default {
  components: {
    "ace-editor": VAceEditor,
    "v-data-table": VDataTable,
  },

  computed: {
    editorOptions() {
      return {
        showPrintMargin: false,
        enableBasicAutocompletion: true,
        enableSnippets: true,
        enableLiveAutocompletion: true,
        autoScrollEditorIntoView: true,
        highlightActiveLine: this.$devMode && this.isFocused,
        highlightGutterLine: this.$devMode && this.isFocused,
        minlines: 1,
        maxLines: Infinity,
      };
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
        this.runCode();
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
    runCode() {
      this.$emit("runCode", this.cellData.id);
    },
    deleteCell() {
      this.$emit("deleteCell", this.cellData.id);
    },
  },
};
</script>
