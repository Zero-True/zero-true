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
      <!-- Render Components -->
      <!-- Render Components -->
      <div v-for="component in UIcomponents" :key="component.id">
        <component :is="component.component" v-bind="component" v-model="component.value"></component>
      </div>
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
import { Response, CellResponse } from './types/response';
import { Slider } from './types/slider';
import { ZTComponent } from './types/zt_component';
import { VSlider } from 'vuetify/lib/components/index.mjs';

export default {
  components: {
    'ace-editor': VAceEditor,
    'v-slider': VSlider

  },
  data() {
    return {
      code: "from zt_backend.models.components.slider import Slider \
\n\ntest_slider = Slider(id='please')",
      UIcomponents: [] as ZTComponent[],  // Typed as an array of ZTComponent interfaces
    };
  },
  methods: {
    async runCode() {
      const codeCell: CodeCell = { code: this.code };
      const request: Request = { cells: [codeCell], components: [] };
      const axiosResponse = await axios.post(import.meta.env.VITE_BACKEND_URL + 'api/runcode', request);
      const response: Response = axiosResponse.data;
      console.log(JSON.stringify(response))
      // Directly assign the component data to components
      this.UIcomponents = response.cells[0].components;
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