<template>
  <v-app style="background-color: #040607">
    <v-app-bar app color="bluegrey" id="appBar">
      <v-btn size="x-large" variant="text" @click="navigateToApp" id ="Navbutton">
        <v-icon start size="x-large" icon="custom:ZTIcon"></v-icon>
        Zero-True
      </v-btn>
      <v-spacer></v-spacer>
      <div v-if="isCodeRunning" class="d-flex align-center">
        <v-progress-circular
          indeterminate
          color="white"
          size="24"
          id = "codeRunProgress"
        ></v-progress-circular>
        <v-chip class="ml-2" color="white" text-color="black" id = "timerChip">
          {{ timer }}ms
        </v-chip>
        <v-chip v-if="$devMode" class="ml-2" color="white" text-color="black" id = "queueLenghtChiptDev">
          Queue Length: {{ requestQueue.length }}
        </v-chip>
        <v-chip v-else class="ml-2" color="white" text-color="black" id = "queueLenghtChipApp">
          Queue Length: {{ componentChangeQueue.length }}
        </v-chip>
        <v-icon
          large
          color="error"
          @click="stopCodeExecution()"
          id = "stopIcon"
        >
          mdi-stop
        </v-icon>
      </div>
      <PackageComponent v-if="$devMode" :dependencies="dependencies"/>
    </v-app-bar>
    <v-main>
      <v-container>
        <v-menu v-if="$devMode" transition="scale-transition">
          <template v-slot:activator="{ props }">
            <v-btn v-bind="props" block>
              <v-row>
                <v-icon color="primary">mdi-plus</v-icon>
              </v-row>
            </v-btn>
          </template>

          <v-list>
            <v-list-item v-for="(item, i) in menu_items" :key="i">
              <v-btn block @click="createCodeCell('', item.title)">{{ item.title }}</v-btn>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-container>
      <v-container v-for="codeCell in notebook.cells">
        <component v-if="codeCell.cellType==='code'"
          :is="getComponent(codeCell.cellType)"
          :cellData="codeCell"
          :completions="completions[codeCell.id]"
          @runCode="runCode"
          @saveCell="saveCell"
          @componentChange="componentValueChange"
          @deleteCell="deleteCell"
          @createCell="createCodeCell"
        />
        <component v-else
          :is="getComponent(codeCell.cellType)"
          :cellData="codeCell"
          @runCode="runCode"
          @saveCell="saveCell"
          @componentChange="componentValueChange"
          @deleteCell="deleteCell"
          @createCell="createCodeCell"
        />
      </v-container>
    </v-main>
  </v-app>
</template>

<script lang="ts">
import axios from "axios";
import { Request, CodeRequest } from "./types/request";
import { ComponentRequest } from "./types/component_request";
import { DeleteRequest } from "./types/delete_request";
import { SaveRequest } from "./types/save_request";
import { CreateRequest, Celltype } from "./types/create_request";
import { ClearRequest } from "./types/clear_request";
import { Notebook, CodeCell, Layout } from "./types/notebook";
import { Dependencies } from "./types/notebook_response";
import CodeComponent from "@/components/CodeComponent.vue";
import MarkdownComponent from "@/components/MarkdownComponent.vue";
import EditorComponent from "@/components/EditorComponent.vue";
import SQLComponent from "@/components/SQLComponent.vue";
import PackageComponent from "@/components/PackageComponent.vue";

export default {
  components: {
    CodeComponent,
    MarkdownComponent,
    EditorComponent,
    SQLComponent,
    PackageComponent
  },

  data() {
    return {
      notebook: {} as Notebook,
      dependencies: {} as Dependencies,
      completions: {} as {[key: string]: any[]},
      ws_url: '',
      notebook_socket: null as WebSocket | null,
      save_socket: null as WebSocket | null,
      run_socket: null as WebSocket | null,
      stop_socket: null as WebSocket | null,
      timer: 0, // The timer value
      timerInterval: null as ReturnType<typeof setInterval> | null, // To hold the timer interval
      isCodeRunning: false,
      requestQueue: [] as any[],
      componentChangeQueue: [] as  any[],
      menu_items: [
          { title: 'Code' },
          { title: 'SQL' },
          { title: 'Markdown' },
          { title: 'Text' },
        ],
      concatenatedCodeCache: {
      lastCellId: '' as string,
      code: '' as string,
      length: 0 as number
    }
    };
  },

  beforeMount() {
    window.addEventListener("beforeunload", this.clearState);
    window.addEventListener("unload", this.clearState);
  },

  beforeUnmount() {
    window.removeEventListener("beforeunload", this.clearState);
    window.removeEventListener("unload", this.clearState);
  },

  async mounted(){
    await this.get_ws_url()
    await this.initializeNotebookSocket()
    await this.initializeRunSocket()
    await this.initializeStopSocket()
    if (this.$devMode){
      await this.initializeSaveSocket()
    }
    this.isCodeRunning = true;
    this.startTimer();
    this.notebook_socket!.send("")
  },

  methods: {
    startTimer() {
      this.timer = 0;
      this.timerInterval = setInterval(() => {
        this.timer++;
      }, 1); // Update every millisecond
    },
    stopTimer() {
      if (this.timerInterval) {
        clearInterval(this.timerInterval);
        this.timerInterval = null;
      }
    },

    async get_ws_url() {
        const response = await axios.get(import.meta.env.VITE_BACKEND_URL + "ws_url");
        this.ws_url = response.data || import.meta.env.VITE_WS_URL
    },

    async runCode(originId: string){
      if (!originId) return;
      const cellRequests: CodeRequest[] = [];
      const requestComponents: { [key: string]: any } = {};
      for (let key in this.notebook.cells) {
        const cellRequest: CodeRequest = {
          id: key,
          code: this.notebook.cells[key].code,
          variable_name: this.notebook.cells[key].variable_name || "",
          cellType: this.notebook.cells[key].cellType,
        };
        for (const c of this.notebook.cells[key].components) {
          if (c.component === 'v-data-table') {
            console.log('v-data-table')
            requestComponents[c.id] = '';
          } else {
            requestComponents[c.id] = c.value;
          }
        }
        cellRequests.push(cellRequest);
      }
      const request: Request = {
        originId: originId,
        cells: cellRequests,
        components: requestComponents,
      };

      if (this.isCodeRunning) {
        const existingRequestIndex = this.requestQueue.findIndex(req => req.originId === originId);
        if (existingRequestIndex !== -1) {
          this.requestQueue[existingRequestIndex] = request;
        } else {
          this.requestQueue.push(request);
        }
        return;
      }
      
      this.sendRunCodeRequest(request)
    },

    sendRunCodeRequest(request: Request) {
      this.isCodeRunning = true;
      this.startTimer();
      this.run_socket!.send(JSON.stringify(request))
    },

    initializeNotebookSocket(){
      this.notebook_socket = new WebSocket(this.ws_url + 'ws/notebook')
      this.notebook_socket!.onmessage = (event) => {
        const response = JSON.parse(event.data)        
        if (response.cell_id){
          if (response.clear_output){
            this.notebook.cells[response.cell_id].output=""
          }
          else{
            this.notebook.cells[response.cell_id].output = this.notebook.cells[response.cell_id].output.concat(response.output)
          }
        }

        else if (response.complete){
          this.isCodeRunning = false;
          this.stopTimer();
        }

        else {
          const cell_response = JSON.parse(response)
          if (cell_response.notebook){
            this.notebook = cell_response.notebook;
            for (let cell_id in this.notebook.cells){
              if (this.notebook.cells[cell_id].cellType==='code'){
                this.completions[cell_id] = []
              }
            }
            this.dependencies = cell_response.dependencies;
          }
          else {
            this.notebook.cells[cell_response.id].components = cell_response.components;
            this.notebook.cells[cell_response.id].layout = cell_response.layout as
              | Layout
              | undefined;
          }
        }
      };
      return new Promise<void>((resolve, reject) => {
        // Resolve the promise when the connection is open
        this.notebook_socket!.onopen = () => {
          console.log("Notebook socket connected");
          resolve();
        };

        // Reject the promise on connection error
        this.notebook_socket!.onerror = (error) => {
          console.error("Notebook socket connection error:", error);
          reject(error);
        };
      });
    },

    initializeRunSocket(){
      this.run_socket = this.$devMode ? new WebSocket(this.ws_url + 'ws/run_code') : new WebSocket(this.ws_url + 'ws/component_run')
      this.run_socket!.onmessage = (event) => {
        const response = JSON.parse(event.data)
        if (!this.$devMode && response.refresh) {
          this.notebookRefresh()
        }

        else if (response.cell_id){
          if (response.clear_output){
            this.notebook.cells[response.cell_id].output=""
          }
          else{
            this.notebook.cells[response.cell_id].output = this.notebook.cells[response.cell_id].output.concat(response.output)
          }
        }

        else if (response.complete){
          this.isCodeRunning = false;
          this.stopTimer();
          if (this.$devMode && this.requestQueue.length > 0){
            const currentRequest = this.requestQueue.shift() || {};
            this.sendRunCodeRequest(currentRequest)
          }
          else if (!this.$devMode && this.componentChangeQueue.length > 0){
            const componentChangeRequest = this.componentChangeQueue.shift() || {};
            const componentRequest: ComponentRequest = {
              originId: componentChangeRequest.originId,
              components: componentChangeRequest.components,
              userId: componentChangeRequest.userId,
            };
            this.sendComponentRequest(componentRequest)
          }
        }

        else {
          const components_response = JSON.parse(response)
          this.notebook.cells[components_response.id].components = components_response.components;
          this.notebook.cells[components_response.id].layout = components_response.layout as
            | Layout
            | undefined;
        }
      };
      return new Promise<void>((resolve, reject) => {
        // Resolve the promise when the connection is open
        this.run_socket!.onopen = () => {
          console.log("Run socket connected");
          resolve();
        };

        // Reject the promise on connection error
        this.run_socket!.onerror = (error) => {
          console.error("Run socket connection error:", error);
          reject(error);
        };
      });
    },

    initializeSaveSocket() {
      this.save_socket = new WebSocket(this.ws_url + 'ws/save_text')
      this.save_socket!.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          // Assuming data is an array of completion objects
          this.completions[data.cell_id] = Array.isArray(data.completions) ? data.completions : [];
        } catch (error) {
          console.error('Error parsing server message:', error);
        }
      };
      return new Promise<void>((resolve, reject) => {
        // Resolve the promise when the connection is open
        this.save_socket!.onopen = () => {
          console.log("Save socket connected");
          resolve();
        };

        // Reject the promise on connection error
        this.save_socket!.onerror = (error) => {
          console.error("Save socket connection error:", error);
          reject(error);
        };
      });
    },

    initializeStopSocket(){
      this.stop_socket = new WebSocket(this.ws_url + 'ws/stop_execution')
      return new Promise<void>((resolve, reject) => {
        // Resolve the promise when the connection is open
        this.stop_socket!.onopen = () => {
          console.log("Stop socket connected");
          resolve();
        };

        // Reject the promise on connection error
        this.stop_socket!.onerror = (error) => {
          console.error("Stop socket connection error:", error);
          reject(error);
        };
      });
    },

    async componentValueChange(originId: string, componentId: string, newValue: any) {
      // Updating the component's value in the notebook
      const requestComponents: { [key: string]: any } = {};
      for (let key in this.notebook.cells) {
        for (const c of this.notebook.cells[key].components) {
          if (c.component === 'v-data-table') {
            requestComponents[c.id] = '';
          } else {
            requestComponents[c.id] = c.value;
          }        }
      }

      // Preparing the component change request
      const componentChangeRequest = {
        originId: originId,
        componentId: componentId,
        components: requestComponents,
        userId: this.notebook.userId,
      };

      // Updating the queue: if the componentId already exists, update the value; otherwise, add to the queue
      // If code is already running, exit the function to wait for the current execution to finish
      if (this.isCodeRunning) {
        const existingRequestIndex = this.componentChangeQueue.findIndex(req => req.componentId === componentId);
        if (existingRequestIndex !== -1) {
          this.componentChangeQueue[existingRequestIndex] = componentChangeRequest;
        } else {
          this.componentChangeQueue.push(componentChangeRequest);
        }
        return;
      }

      const componentRequest: ComponentRequest = {
        originId: componentChangeRequest.originId,
        components: componentChangeRequest.components,
        userId: componentChangeRequest.userId,
      };

      this.sendComponentRequest(componentRequest)
    },

    sendComponentRequest(componentRequest: ComponentRequest) {
      this.isCodeRunning = true;
      this.startTimer();
      this.run_socket!.send(JSON.stringify(componentRequest))
    },

    async notebookRefresh(){//TODO: Fix this
      this.isCodeRunning = true;
      this.startTimer();
      this.notebook_socket!.send('start')
    },

    navigateToApp() {
      window.open("https://zero-true.com/");
    },

    clearState: function clearState() {
      const clearRequest: ClearRequest = { userId: this.notebook.userId };
      axios.post(
        import.meta.env.VITE_BACKEND_URL + "api/clear_state",
        clearRequest
      );
    },

    async createCodeCell(position_key: string, cellType: string) {
      const cellRequest: CreateRequest = { cellType: cellType.toLowerCase() as Celltype, position_key: position_key };
      const response = await axios.post(
        import.meta.env.VITE_BACKEND_URL + "api/create_cell",
        cellRequest
      );
      const cell: CodeCell = response.data;
      let cells: Record<string, CodeCell> = {};
      if (!position_key){
        cells[cell.id] = cell
      }
      for (let key in this.notebook.cells) {
        cells[key] = this.notebook.cells[key]
        if (position_key===key){
          cells[cell.id] = cell
        }
      }
      if (cell.cellType==='code'){
        this.completions[cell.id] = []
      }
      this.notebook.cells = cells;
    },

    async deleteCell(cellId: string) {
      const deleteRequest: DeleteRequest = { cellId: cellId };
      await axios.post(
        import.meta.env.VITE_BACKEND_URL + "api/delete_cell",
        deleteRequest
      );
      if (this.notebook.cells[cellId].cellType==='code'){
        delete this.completions[cellId]
      }
      delete this.notebook.cells[cellId];
    },

    async saveCell(cellId: string, text: string, line: string, column: string) {
      // Check if the current cell is a code cell
      if (this.notebook.cells[cellId].cellType === 'code') {
        if (this.concatenatedCodeCache.lastCellId !== cellId) {
            let concatenatedCode = '';
            let length = 0
            for (let key in this.notebook.cells) {
              if (key === cellId) break;
              if (this.notebook.cells[key].cellType === 'code') {
                concatenatedCode += this.notebook.cells[key].code+'\n';
                length += this.notebook.cells[key].code.split(/\r\n|\r|\n/).length
              }
            }

            // Update the cache
            this.concatenatedCodeCache = {
              lastCellId: cellId,
              code: concatenatedCode,
              length: length
            };
          }
      }
      // The rest of the saveCell method remains unchanged
      const saveRequest: SaveRequest = {
        id: cellId,
        text: text, // Use the concatenated code from previous cells
        cellType: this.notebook.cells[cellId].cellType,
        line:  this.concatenatedCodeCache.length+line,
        column: column,
        code_w_context: this.concatenatedCodeCache.code+text
      };
      this.save_socket!.send(JSON.stringify(saveRequest))
    },

    async stopCodeExecution(){
      if (this.$devMode) {
        this.requestQueue = []
        this.stop_socket!.send("")
      }
      else {
        this.componentChangeQueue = []
        this.stop_socket!.send(this.notebook.userId)
      }
      this.isCodeRunning = false;
      this.stopTimer();
    },

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
  },
};
</script>

<style>
.cm-editor {
  height: auto !important;
}
</style>
