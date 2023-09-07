<template>
  <v-card flat>
    <div class="code-editor-container">
      <!-- Display the ace-editor -->
      <ace-editor
          v-model:value="code"
          ref="editor"
          class="editor"
          theme="dracula"
          lang="python"
          :options="{
            showPrintMargin: false,
            enableBasicAutocompletion: true,
            enableSnippets: true,
            enableLiveAutocompletion: true
          }"
      ></ace-editor>
      <!-- Run Button -->
      <v-btn color="primary" class="run-button" @click="runCode">Run</v-btn>
    </div>
  </v-card>
</template>

<script lang="ts">
import { VAceEditor } from 'vue3-ace-editor';
import 'ace-builds/src-noconflict/mode-python';
import 'ace-builds/src-noconflict/snippets/python';
import 'ace-builds/src-noconflict/ext-language_tools';
import 'ace-builds/src-noconflict/theme-dracula';
import axios from 'axios';
import { Request, CodeCell } from './types/request';

export default {
  components: {
    'ace-editor': VAceEditor,
  },
  data() {
    return {
      code: 'print("Hello, World!")',  // Default code in the editor
    };
  },
  methods: {
    async runCode() {
      const codeCell: CodeCell = {code: this.code}
      const request: Request = {cells: [codeCell]}
      const respone = axios.post(import.meta.env.VITE_BACKEND_URL + 'api/runcode', request);
    },
  }
}
</script>
<style scoped>
.editor {
  height: 300px;
  width: 100%;
  margin-bottom: 20px;
}
.run-button {
  margin-bottom: 20px;
}
</style>