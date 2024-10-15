<template>
  <cell
    cell-type="markdown"
    :cell-id="cellData.id" 
    :is-dev-mode="$devMode && !isAppRoute && !isMobile"
    :hide-cell="(cellData.hideCell as boolean)"
    :cell-name="(cellData.cellName as string)"
    @delete="deleteCell"
    @save="saveCell"
    @addCell="e => createCell(e)"
  >
    <template v-slot:code>
      <codemirror
        v-if="$devMode && !isMobile"
        v-model="cellData.code"
        :style="{ height: '400px' }"
        :autofocus="true"
        :indent-with-tab="true"
        :tab-size="2"
        :viewportMargin="Infinity"
        :extensions="extensions"
        @keyup="saveCell"
      />
    </template>
    <template v-slot:outcome>
      <div class="markdown-content" v-html="compiledMarkdown"></div>
    </template>
  </cell>
</template>

<script lang="ts">
import type { PropType } from "vue";
import { marked } from 'marked';
import { Codemirror } from 'vue-codemirror'
import { markdown } from '@codemirror/lang-markdown'
import { oneDark } from '@codemirror/theme-one-dark'
import { autocompletion } from '@codemirror/autocomplete'
import { CodeCell } from "@/types/notebook";
import AddCell from '@/components/AddCell.vue'
import { useRoute } from 'vue-router'
import Cell from '@/components/Cell.vue'

export default {
  components: {
    "add-cell": AddCell,
    "cell": Cell,
    "codemirror": Codemirror,
  },
  computed: {
    extensions() {return [markdown(), oneDark, autocompletion({ override: [] })]},

    compiledMarkdown() {
      const pasrsed_markdown = marked.parse(this.cellData.code,)
      return pasrsed_markdown;
    },
    isAppRoute() {
      const route = useRoute()
      return route.path === '/app'
    },
    isMobile() {
      return this.$vuetify.display.mobile
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
  inheritAttrs: false,
  emits: ['saveCell', 'deleteCell', 'createCell'],
  props: {
    cellData: {
      type: Object as PropType<CodeCell>,
      required: true,
    },
  },
  methods: {
    saveCell() {
      if (!this.$devMode) return
      this.$emit("saveCell", this.cellData.id, this.cellData.code, '', '');
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

<style scoped>
 
.markdown-content {
  /* General text styling */
  font-family: Arial, sans-serif;
  line-height: 1.6;
  color: #ffffff;}
  

  /* Headings */
  .markdown-content :deep(h1),.markdown-content :deep(h2), .markdown-content :deep(h3), .markdown-content :deep(h4), .markdown-content :deep(h5), .markdown-content :deep(h6) {
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    font-weight: bold;
    line-height: 1.3;
  }

  /* Paragraphs */
  .markdown-content :deep(p) {
    margin-top: 0;
    margin-bottom: 1em;
  }

  /* Lists */
  .markdown-content :deep(ul), 
  .markdown-content :deep(ol) {
    margin-top: 0.5em;
    margin-bottom: 0.5em;
  }

  .markdown-content :deep(ul) {
    list-style-type: disc;
    margin-left: 5px;
  }

  .markdown-content :deep(ol) {
    list-style-type: decimal;
    margin-left: 20px;
  }

  .markdown-content :deep(li) {
    margin-bottom: 0.25em;
  }

  /* Handle all levels of nested lists */
.markdown-content :deep(li > ul),
.markdown-content :deep(li > ol) {
  margin-top: 0.25em;
  margin-bottom: 0.25em;
  margin-left: 20px;

}

/* Unordered list styles */
.markdown-content :deep(ul) {
  list-style-type: disc
}
/* Ordered list styles */
.markdown-content :deep(ol) {
  list-style-type: decimal;
}

  /* Links */
  .markdown-content :deep(a) {
    color: #007bff;
    text-decoration: none;
  }
  .markdown-content :deep(a:hover) {
    text-decoration: underline;
  }
  

  /* Images */
  .markdown-content :deep(img) {
    max-width: 100%;
    height: auto;
  }

  
  /* Blockquotes */
  .markdown-content :deep(blockquote) {
    margin: 0;
    padding-left: 1em;
    color: #6a737d;
    border-left: 0.25em solid #dfe2e5;
  }

</style>