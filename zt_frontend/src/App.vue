<template>
  <v-app style="background-color: #040607;">
    <v-app-bar app color="bluegrey">
      <v-btn size="x-large" variant="text" @click="navigateToApp">
        <v-icon start size="x-large" icon="custom:ZTIcon"></v-icon>
        Zero-True
      </v-btn>
    </v-app-bar>
    <v-main>
      <v-container v-for="codeCell in notebook.cells" >
        <component
          :style="{ '--cursor-opacity': $devMode ? '100' : '0' }"
          :is="getComponent(codeCell.cellType)"
          :cellData = codeCell
          @runCode="runCode"
          @componentChange="componentValueChange"
          @deleteCell="deleteCell"/>
      </v-container>
      <v-toolbar v-if="$devMode" color="bluegrey" >
        <v-btn variant="flat" color="accent" @click="createCodeCell('code')">Add Code Cell</v-btn>
        <v-spacer/>
        <v-btn variant="flat" color="accent" @click="createCodeCell('sql')">Add SQL Cell</v-btn>
        <v-spacer/>
        <v-btn variant="flat" color="accent" @click="createCodeCell('markdown')">Add Markdown Cell</v-btn>
        <v-spacer/>
        <v-btn variant="flat" color="accent" @click="createCodeCell('text')">Add Text Cell</v-btn>
      </v-toolbar>
    </v-main>
  </v-app>
</template>


<script lang="ts">
import axios from 'axios';
import { Request, CodeRequest } from './types/request';
import { ComponentRequest } from './types/component_request';
import { DeleteRequest } from './types/delete_request';
import { CreateRequest, Celltype } from './types/create_request';
import { Response } from './types/response';
import { Notebook, CodeCell, ZTLayout } from './types/notebook';
import CodeComponent from '@/components/CodeComponent.vue';
import MarkdownComponent from '@/components/MarkdownComponent.vue';
import EditorComponent from '@/components/EditorComponent.vue';
import SQLComponent from '@/components/SQLComponent.vue';

export default {
  components: {
    CodeComponent,
    MarkdownComponent,
    EditorComponent,
    SQLComponent
  },
  data() {
    return {
      notebook: {} as Notebook,
    };
  },

  async created() {
      const response = await axios.get(import.meta.env.VITE_BACKEND_URL + 'api/notebook')
      this.notebook = response.data
  },

  methods: {
    async runCode(originId: string) {
      const cellRequests: CodeRequest[] = []
      const requestComponents: { [key: string]: any } = {};
      for (let key in this.notebook.cells){
        const cellRequest: CodeRequest = {
          id: key, 
          code: this.notebook.cells[key].code, 
          variable_name: this.notebook.cells[key].variable_name, 
          cellType: this.notebook.cells[key].cellType,
        }
        for (const c of this.notebook.cells[key].components){
          requestComponents[c.id] = c.value
        }
        cellRequests.push(cellRequest)
      }
      const request: Request = { originId: originId, cells: cellRequests, components: requestComponents, userId: this.notebook.userId }
      const axiosResponse = await axios.post(import.meta.env.VITE_BACKEND_URL + 'api/runcode', request)
      const response: Response = axiosResponse.data
      for (const cellResponse of response.cells){
        this.notebook.cells[cellResponse.id].components = cellResponse.components
        this.notebook.cells[cellResponse.id].output = cellResponse.output
        this.notebook.cells[cellResponse.id].layout = cellResponse.layout as ZTLayout | undefined;

      }
    },

    async componentValueChange(originId: string, componentId: string, newValue: any){
      const componentRequest: ComponentRequest = {originId: originId, componentId: componentId, componentValue: newValue,userId: this.notebook.userId}
      const axiosResponse = await axios.post(import.meta.env.VITE_BACKEND_URL + 'api/component_run', componentRequest)
      const response: Response = axiosResponse.data
      for (const cellResponse of response.cells){
        this.notebook.cells[cellResponse.id].components = cellResponse.components
        this.notebook.cells[cellResponse.id].output = cellResponse.output
        this.notebook.cells[cellResponse.id].layout = cellResponse.layout as ZTLayout | undefined;

      }
    },

    navigateToApp(){
      console.log('navigate')
    },

    async createCodeCell(cellType: string){
      const cellRequest: CreateRequest = {cellType: cellType as Celltype}
      const response = await axios.post(import.meta.env.VITE_BACKEND_URL + 'api/create_cell', cellRequest);
      const cell: CodeCell = response.data
      this.notebook.cells[cell.id] = cell
    },

    async deleteCell(cellId: string){
      const deleteRequest: DeleteRequest = {cellId: cellId}
      await axios.post(import.meta.env.VITE_BACKEND_URL + 'api/delete_cell', deleteRequest);
      delete this.notebook.cells[cellId]
    },

    getComponent(cellType: string){
      switch (cellType) {
        case 'code':
          return 'CodeComponent';
        case 'text':
          return 'EditorComponent';
        case 'markdown':
          return 'MarkdownComponent';
        case 'sql':
          return 'SQLComponent';
        default:
          throw new Error(`Unknown component type: ${cellType}`);
      }
    }
  }
}
</script>

<style>
.editor {
    background-color: #1B2F3C;
    filter: none;
    height: 300px;
    width: 100%;
    margin-bottom: 20px;
}
.editor .ace_gutter {
    background: #1B2F3C;
}
.editor .ace_active-line {
    background: #0E1B23 !important;
}
.editor .ace_gutter-active-line {
    background: #0E1B23 !important;
}

.editor .ace_cursor {
  opacity: var(--cursor-opacity) !important;
}
</style>