<template>
  <v-app>
    <v-app-bar 
      app 
      color="bluegrey-darken-4"
      extension-height="112" 
      id="appBar"
    >
      <v-btn size="x-large" variant="text" @click="navigateToApp" id ="Navbutton">
        <v-icon start size="x-large" :icon="`ztIcon:${ztAliases.logo}`"></v-icon>
      </v-btn>
      <div class="click-edit">
        <div class="click-edit__show-text" v-if="!editingProjectName">
          <h5 class="click-edit__name text-h5">{{ notebookName ?? 'Zero True' }}</h5> 
          <v-btn
            color="bluegrey-darken-1"
            :icon="`ztIcon:${ztAliases.edit}`"
            @click="toggleProjectName"
          />
        </div> 
        
        <div class="click-edit__edit-field-wrapper" v-if="editingProjectName">
          <v-text-field 
            v-model="notebookName"   
            placeholder="Zero True"
            density="compact" 
            variant="plain"
            hide-details
            ref="projectNameField" 
            class="click-edit__edit-field" 
          />
          <v-btn
            color="bluegrey-darken-1"
            :icon="`ztIcon:${ztAliases.save}`"
            @click="saveProjectName"
          />
          <v-btn
            color="bluegrey-darken-1"
            icon="$close"
            @click="toggleProjectName"
          />
        </div> 
      </div>
      <div class="toggle-group" v-if="!isMobile">
        <v-btn-toggle
          :multiple="false"
          mandatory
        >
          <v-btn
            :color="!isAppRoute ? 'primary': 'bluegrey-darken-1'"
            :variant="!isAppRoute ? 'flat': 'text'" 
            :class="{ 'text-bluegrey-darken-4' : !isAppRoute }"
            :prepend-icon="`ztIcon:${ztAliases.notebook}`"
            to="/"
          >
          Notebook</v-btn>
          <v-btn 
            :color="isAppRoute ? 'primary': 'bluegrey-darken-1'"
            :variant="isAppRoute ? 'flat': 'text'" 
            :class="{ 'text-bluegrey-darken-4' : isAppRoute }"
            :prepend-icon="`ztIcon:${ztAliases.monitor}`"
            to="/app"
          >App</v-btn>
        </v-btn-toggle>
      </div>
      
      <template v-slot:append>
        <v-col class="d-flex justify-end">
          <div>
            <!-- <v-btn :icon="`ztIcon:${ztAliases.undo}`"></v-btn>
            <v-btn :icon="`ztIcon:${ztAliases.redo}`"></v-btn>
            <v-btn :icon="`ztIcon:${ztAliases.message}`"></v-btn> -->
            <PackageComponent v-if="$devMode" :dependencies="dependencies"/>
            <!-- <v-btn :icon="`ztIcon:${ztAliases.play}`"></v-btn>
            <v-btn
              :prepend-icon="`ztIcon:${ztAliases.play}`"
              variant="flat"
              ripple
              color="primary"
              class="text-bluegrey-darken-4"
            >Share</v-btn> -->
          </div> 
        </v-col>
      </template>
    </v-app-bar>
    <v-main :scrollable="false">
      <CodeCellManager 
        :notebook="notebook"
        :completions="completions"
        @runCode="runCode"
        @saveCell="saveCell"
        @componentValueChange="componentValueChange"
        @deleteCell="deleteCell"
        @createCell="createCodeCell"
       />
    </v-main>
    <v-footer 
      app
      class="footer bg-bluegrey-darken-4 text-bluegrey"
    >
      <div class="footer__left-container">
        <span>
          <v-icon
            class="footer__code-version-icon"
            :icon="`ztIcon:${ztAliases.cubic}`" 
          />
          <span>Python {{pythonVersion}}</span>
        </span> 
        <v-icon class="dot-divider" :icon="`ztIcon:${ztAliases.dot}`"/>
        <span>Zero-True {{ztVersion}}</span>
        <v-icon class="dot-divider" :icon="`ztIcon:${ztAliases.dot}`"/>
        <span>{{ cellLength }} cells</span>
      </div> 
      <div class="footer__right-container">
        <div class="footer__queue-length-wrapper" v-if="isCodeRunning">
          <v-progress-circular
            indeterminate
            color="bluegrey"
            size="17"
            class="footer__code-running-loader"
            id = "codeRunProgress"
          ></v-progress-circular>
          <v-chip density="comfortable">{{ timer }}ms</v-chip>
          <v-btn 
            class="footer__queue-length-btn"
            density="compact"
            append-icon="mdi:mdi-chevron-down"
            rounded
            :disabled="queueLength === 0"
            variant="flat"
          >
            Queue Length: {{ queueLength }}
            <v-menu 
              activator="parent"
              >
              <v-list class="footer__queue-list">
                <v-list-item
                  v-for="(item, i) in runningQueue"
                  :key="i"
                  class="footer__queue-list-item"
                >
                  <span class="text-bluegrey">Python #2</span>
                  <template v-slot:append>
                    <v-icon icon="$done" color="success"/>
                  </template>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-btn>
        </div> 
        
        <div class="footer__status-wrapper">
          <!-- <span>
            <v-icon 
              :icon="`ztIcon:${ztAliases.clock}`" 
            />
            Saved 5mins ago
          </span> -->
          <!-- <v-icon class="dot-divider" :icon="`ztIcon:${ztAliases.dot}`"/> -->
          <div
            v-if="isCodeRunning"  
            class="footer__status"
          >
            <v-icon :icon="`ztIcon:${ztAliases.status}`" />
            <span>Running</span>
          </div>
          <div
            v-if="!isCodeRunning"
            class="footer__status footer__status--error"
          >
            <v-icon :icon="`ztIcon:${ztAliases.status}`" />
            <span>Stopped</span>
          </div>
          <v-btn 
            v-if="isCodeRunning"
            density="comfortable"
            :icon="`ztIcon:${ztAliases.stop}`"     
            color="bluegrey"
            variant="plain"
            :ripple="false" 
            @click="stopCodeExecution()"
            rounded
          >
          </v-btn>
        </div> 
      </div> 
    </v-footer>
  </v-app>
</template>

<script lang="ts">
import axios from "axios";
import { nextTick } from 'vue';
import { useRoute } from "vue-router";
import { Request, CodeRequest } from "./types/request";
import { ComponentRequest } from "./types/component_request";
import { DeleteRequest } from "./types/delete_request";
import { SaveRequest } from "./types/save_request";
import { CreateRequest, Celltype } from "./types/create_request";
import { ClearRequest } from "./types/clear_request";
import { NotebookNameRequest } from "./types/notebook_name_request";
import { Notebook, CodeCell, Layout } from "./types/notebook";
import { Dependencies } from "./types/notebook_response";
import CodeComponent from "@/components/CodeComponent.vue";
import MarkdownComponent from "@/components/MarkdownComponent.vue";
import EditorComponent from "@/components/EditorComponent.vue";
import SQLComponent from "@/components/SQLComponent.vue";
import PackageComponent from "@/components/PackageComponent.vue";
import CodeCellManager from "./components/CodeCellManager.vue";
import type { VTextField } from "vuetify/lib/components/index.mjs";
import { ztAliases } from '@/iconsets/ztIcon'

export default {
  components: {
    CodeComponent,
    MarkdownComponent,
    EditorComponent,
    SQLComponent,
    PackageComponent,
    CodeCellManager
  },

  data() {
    return {
      editingProjectName: false, 
      notebook: {} as Notebook,
      notebookName: '',
      dependencies: {} as Dependencies,
      completions: {} as {[key: string]: any[]},
      ws_url: '',
      pythonVersion: '',
      ztVersion: '',
      notebook_socket: null as WebSocket | null,
      save_socket: null as WebSocket | null,
      run_socket: null as WebSocket | null,
      stop_socket: null as WebSocket | null,
      timer: 0, // The timer value
      timerInterval: null as ReturnType<typeof setInterval> | null, // To hold the timer interval
      isCodeRunning: false,
      requestQueue: [] as any[],
      componentChangeQueue: [] as  any[],
      concatenatedCodeCache: {
        lastCellId: '' as string,
        code: '' as string,
        length: 0 as number,
      },
      ztAliases
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
    await this.get_env_data()
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

  computed: {
    isAppRoute() {
      const route = useRoute()
      return route.path === '/app'
    }, 
    isMobile() {
      return this.$vuetify.display.mobile
    },
    cellLength() {
      return this.notebook.cells ? Object.keys(this.notebook.cells).length : 0
    },
    runningQueue() {
      return this.$devMode ? this.requestQueue : this.componentChangeQueue; 
    },
    queueLength() {
      return this.runningQueue.length; 
    }
  },

  methods: {
    toggleProjectName() {
      this.editingProjectName = !this.editingProjectName
      nextTick(() => {
        if (this.editingProjectName) {
          (this.$refs.projectNameField as VTextField).focus();
        }
      }) 
    },
    async saveProjectName() {
      const notebookNameRequest: NotebookNameRequest = {
        notebookName: this.notebookName,
      };
      await axios.post(import.meta.env.VITE_BACKEND_URL + "api/notebook_name_update", notebookNameRequest);
      document.title = this.notebookName
      this.editingProjectName = !this.editingProjectName
    },
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

    async get_env_data() {
        const response = await axios.get(import.meta.env.VITE_BACKEND_URL + "env_data");
        const envData = response.data
        this.ws_url = envData.ws_url || import.meta.env.VITE_WS_URL
        this.pythonVersion = envData.python_version
        this.ztVersion = envData.zt_version
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
        if (response.notebook_name) {
          this.notebookName = response.notebook_name
          document.title = this.notebookName
        }
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
          const cell_response = typeof response === 'string' ? JSON.parse(response) : response
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
            if (this.notebook.cells && this.notebook.cells[cell_response.id])  {
              this.notebook.cells[cell_response.id].components = cell_response.components;
              this.notebook.cells[cell_response.id].layout = cell_response.layout as
                | Layout
                | undefined;
            }
            
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
      console.log('creating cell')
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

<style lang="scss" scoped>
@import '@/styles/mixins.scss';
.cm-editor {
  height: auto !important;
}

.click-edit {
  max-width: 200px;
  width: 100%;
  &__name {
    font-weight: normal;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  &__show-text,
  &__edit-field-wrapper {
    display: flex;
    align-items: center;
  }

  &__edit-field {
    margin-top: -11px; 
    & :deep(.v-field__input) {
      font-size: 1.5rem;
      letter-spacing: normal;
    }
  }
  @include sm {
    max-width: 250px;
  }
  @include lg {
    max-width: 320px;
  }
}
.footer {
  display: flex;
  justify-content: space-between;
  flex-direction: column;

  &__left-container,
  &__right-container {
    display: flex;
    width: 100%;
    @include md {
      align-items: center;
      width: auto;
    }
  }
  
  &__right-container {
    align-items: center;
    flex-direction: column;
    justify-content: flex-start; 
    @include sm {
      flex-direction: row;
    }
  }
  
  &__left-container {
    flex-direction: column;
    margin: 0 0 20px 0px;
    @include sm {
      margin: 0;
      flex-direction: row;
    }
  }

  &__queue-length-wrapper {
    display: flex;
    justify-content: flex-start;
    width: 100%;
    @include sm {
      width: auto;
    }
  }

  .dot-divider {
    display: none;
    margin: 0 5px;
    @include sm {
      display: flex;
      margin: 0 16px;
    }
    @include lg {
      margin: 0 16px;
    }
    @include xl {
      margin: 0 24px;
    }
  }
  &__status-wrapper {
    display: flex;
    justify-content: flex-start;
    width: 100%;
    align-items: center;
    .dot-divider {
      display: none;
      @include md {
        display: flex;
      }
    }
  }

  
  &__code-version-icon {
    margin-right: 0px;
    margin-left: -5px;
    @include sm {
      margin-right: 12px;
    }
  }
  &__queue-length-btn {
    margin: 0 2px 0 2px;
    @include md {
      margin: 0 8px 0 24px;
    }
  }
  &__code-running-loader {
    margin-right: 10px;
    @include lg {
      margin-right: 10px;
    }
  }
  &__queue-list {
    font-size: 0.625rem;
  }
  &__queue-list-item {
    &--pending {
      color: rgba(var(--v-theme-bluegrey-darken-2));
    }
  }
  &__status {
    color: rgba(var(--v-theme-success));
    &--error {
      color: rgba(var(--v-theme-error));
    }
  }
  @include md {
    flex-direction: row;
    height: 42px;
  }
}

.toggle-group {
  display: flex;
  justify-content: center;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}
</style>
