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
    <codemirror
      v-if="$devMode"
      v-model="cellData.code"
      :style="{ height: '400px' }"
      :autofocus="true"
      :indent-with-tab="true"
      :tab-size="2"
      :viewportMargin="Infinity"
      :extensions="extensions"
      @focus="handleFocus(true)"
      @blur="handleFocus(false)"
    />
    <div v-if="$devMode">
      <p class="text-caption text-disabled text-right">
        CTRL+Enter to save</p>
    </div>
    <div class="markdown-content" v-html="compiledMarkdown"></div>
  </v-card>
  <v-menu transition="scale-transition">
    <template v-slot:activator="{ props }">
      <v-btn v-bind="props" block>
        <v-row>
          <v-icon color="primary">mdi-plus</v-icon>
        </v-row>
      </v-btn>
    </template>

    <v-list>
      <v-list-item v-for="(item, i) in items" :key="i">
        <v-btn block @click="createCell(item.title)">{{ item.title }}</v-btn>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script lang="ts">
import type { PropType } from "vue";
import { marked } from 'marked';
import { Codemirror } from 'vue-codemirror'
import { markdown } from '@codemirror/lang-markdown'
import { oneDark } from '@codemirror/theme-one-dark'
import { EditorView } from '@codemirror/view'
import { autocompletion, CompletionResult, CompletionContext } from '@codemirror/autocomplete'
import { CodeCell } from "@/types/notebook";

export default {
  components: {
    "codemirror": Codemirror,
  },
  computed: {
    extensions() {return [markdown(), oneDark, autocompletion({ override: [] })]},

    compiledMarkdown() {
      const pasrsed_markdown = marked.parse(this.cellData.code,)
      return pasrsed_markdown;
    },
  },
  data() {
    return {
      isFocused: false, // add this line to keep track of the focus state
      items: [
        { title: 'Code' },
        { title: 'SQL' },
        { title: 'Markdown' },
        { title: 'Text' },
      ],
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
      this.isFocused = state;
    },
    saveCell() {
      this.$emit("saveCell", this.cellData.id);
    },
    deleteCell() {
      this.$emit("deleteCell", this.cellData.id);
    },
    createCell(cellType: string){
      this.$emit("createCell", this.cellData.id, cellType);
    }
  },
};
</script>

<style>
 
.markdown-content {
  /* General text styling */
  font-family: Arial, sans-serif;
  line-height: 1.6;
  color: #ffffff;}
  

  /* Headings */
  .markdown-content   h1, h2, h3, h4, h5, h6 {
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    font-weight: bold;
    line-height: 1.3;
  }

  /* Paragraphs */
  .markdown-content p {
    margin-top: 0;
    margin-bottom: 1em;
  }

  /* Lists */
  .markdown-content ul, ol {
    padding-left: 20px;
    margin-top: 0.5em;
    margin-bottom: 0.5em;
  }

  .markdown-content ul {
    list-style-type: disc;
  }

  .markdown-content ol {
    list-style-type: decimal;
  }

  .markdown-content li {
    margin-bottom: 0.25em;
  }

  /* Links */
  .markdown-content a {
    color: #007bff;
    text-decoration: none;
  }
  .markdown-content a:hover {
    text-decoration: underline;
  }

  /* Images */
  .markdown-content img {
    max-width: 100%;
    height: auto;
  }

  
  /* Blockquotes */
  .markdown-content blockquote {
    margin: 0;
    padding-left: 1em;
    color: #6a737d;
    border-left: 0.25em solid #dfe2e5;
  }

</style>