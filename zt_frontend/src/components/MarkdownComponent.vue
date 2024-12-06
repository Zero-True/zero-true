<template>
  <cell
    cell-type="markdown"
    :cell-id="cellData.id" 
    :is-dev-mode="$devMode && !isAppRoute && !isMobile"
    :hide-cell="(cellData.hideCell as boolean)"
    :cell-name="(cellData.cellName as string)"
    :cell-has-output=hasCellContent
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
        :tab-size="4"
        :viewportMargin="Infinity"
        :extensions="extensions"
        @keyup="saveCell"
        @ready="handleReady"
      />
    </template>
    <template v-slot:outcome>
      <div class="markdown-content" v-html="compiledMarkdown"></div>
    </template>
  </cell>
</template>

<script lang="ts">
import type { PropType, ShallowRef } from "vue";
import { marked } from 'marked';
import { Codemirror } from 'vue-codemirror'
import { markdown } from '@codemirror/lang-markdown'
import { oneDark } from '@codemirror/theme-one-dark'
import { autocompletion } from '@codemirror/autocomplete'
import { CodeCell } from "@/types/notebook";
import AddCell from '@/components/AddCell.vue'
import { useRoute } from 'vue-router'
import Cell from '@/components/Cell.vue'
import {EditorView, keymap} from "@codemirror/view";
import {Prec} from "@codemirror/state";


export default {
  components: {
    "add-cell": AddCell,
    "cell": Cell,
    "codemirror": Codemirror,
  },

  setup() {
    const view: ShallowRef<EditorView | null> = shallowRef(null);
    const handleReady = (payload: any) => {
      view.value = payload.view;
    };

    return { view, handleReady };
  },
  computed: {
    hasCellContent() {
    const hasOutput = Boolean(this.cellData.code?.trim());
    return hasOutput
  },
    extensions() {
      const keyMap = keymap.of([
        {
          key: 'ArrowUp',
          run: (view) => {
            if (view.state.selection.main.from === 0) {
              this.$emit('navigateToCell', this.cellData.id, 'up');
              return true;
            }
            return false;
          },
        },
        {
          key: 'ArrowDown',
          run: (view) => {
            if (view.state.selection.main.to === view.state.doc.length) {
              this.$emit('navigateToCell', this.cellData.id, 'down');
              return true;
            }
            return false;
          },
        }
      ]);
      
    return [Prec.highest(keyMap),markdown(), oneDark, autocompletion({ override: [] })]
    
    },

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
  emits: ['saveCell', 'deleteCell', 'createCell','navigateToCell'],
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
    },
    getEditorView() {
      return this.view || null;
    },
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
    margin-bottom: 0.2em;
    font-weight: bold;
    line-height: 1.3;
  }

  /* Paragraphs */
  .markdown-content :deep(p) {
    margin-top: 0;
    margin-bottom: 0.2em;
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