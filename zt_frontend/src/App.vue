<template>
  <v-app>
    <v-app-bar app color="primary">
      <v-app-bar-title class="white--text">
        <v-btn icon @click="navigateToApp">
        </v-btn>
        Zero-True</v-app-bar-title>
    </v-app-bar>
    <v-main>
      <v-container v-for="codeCell in notebook.cells" >
        <CodeComponent 
          :cellData = codeCell
          @runCode="runCode"/>
      </v-container>
      <v-toolbar color="secondary">
        <v-btn small color="primary" @click="createCodeCell">Add Code Cell</v-btn>
        <v-spacer></v-spacer>
        <v-btn small color="primary">Add Markdown Cell</v-btn>
      </v-toolbar>
    </v-main>
  </v-app>
</template>


<script lang="ts">
import axios from 'axios';
import { Request, CodeRequest } from './types/request';
import { Response } from './types/response';
import { Notebook, CodeCell } from './types/notebook';
import CodeComponent from '@/components/CodeComponent.vue';

export default {
  components: {
    CodeComponent
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
    async runCode() {
      const cellRequests: CodeRequest[] = []
      const requestComponents: { [key: string]: any } = {};
      for (let key in this.notebook.cells){
        const cellRequest: CodeRequest = {id: key, code: this.notebook.cells[key].code}
        for (const c of this.notebook.cells[key].components){
          requestComponents[c.id] = c.value
        }
        //requestComponents.push.apply(requestComponents, this.notebook.cells[key].components)
        cellRequests.push(cellRequest)
      }
      const request: Request = { cells: cellRequests, components: requestComponents }
      const axiosResponse = await axios.post(import.meta.env.VITE_BACKEND_URL + 'api/runcode', request)
      const response: Response = axiosResponse.data
      for (const cellResponse of response.cells){
        this.notebook.cells[cellResponse.id].components = cellResponse.components
        this.notebook.cells[cellResponse.id].output = cellResponse.output
      }
    },

    navigateToApp(){
      console.log('navigate')
    },

    async createCodeCell(){
      const response = await axios.post(import.meta.env.VITE_BACKEND_URL + 'api/create_cell');
      const cell: CodeCell = response.data
      this.notebook.cells[cell.id] = cell
    }
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