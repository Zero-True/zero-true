<template>
  <v-app>
    <v-app-bar
      app
      color="bluegrey-darken-4"
      height="51"
      id="appBar"
      class="zt-app-bar"
    >
      <v-btn
        size="x-large"
        :ripple="false"
        :icon="`ztIcon:${ztAliases.logo}`"
        variant="plain"
        @click="navigateToApp"
        id="Navbutton"
        class="logo-btn"
      >
      </v-btn>
      <div class="click-edit" v-if="$devMode && !isAppRoute">
        <div class="click-edit__show-text" v-if="!editingProjectName">
          <h5
            class="click-edit__name text-ellipsis text-h5"
            @click="toggleProjectName"
          >
            {{ notebookName }}
          </h5>
        </div>

        <div class="click-edit__edit-field-wrapper" v-if="editingProjectName">
          <v-text-field
            v-model="notebookEditName"
            placeholder="Zero True"
            density="compact"
            variant="plain"
            hide-details
            ref="projectNameField"
            class="click-edit__edit-field"
            @keydown.enter="saveProjectName"
            @update:focused="
              (focused) => {
                if (!focused) saveProjectName();
              }
            "
          />
        </div>
      </div>
      <h5 v-else class="text-ellipsis text-h5">{{ notebookName }}</h5>
      <div class="toggle-group" v-if="$devMode && !isMobile">
        <v-btn-toggle :multiple="false" density="compact" mandatory>
          <v-btn
            :color="!isAppRoute ? 'primary' : 'bluegrey-darken-1'"
            :variant="!isAppRoute ? 'flat' : 'text'"
            :class="{ 'text-bluegrey-darken-4': !isAppRoute }"
            :prepend-icon="`ztIcon:${ztAliases.notebook}`"
            to="/"
            id="notebookBtn"
          >
            Notebook</v-btn
          >
          <v-btn
            :color="isAppRoute ? 'primary' : 'bluegrey-darken-1'"
            :variant="isAppRoute ? 'flat' : 'text'"
            :class="{ 'text-bluegrey-darken-4': isAppRoute }"
            :prepend-icon="`ztIcon:${ztAliases.monitor}`"
            to="/app"
            id="appBtn"
            >App</v-btn
          >
        </v-btn-toggle>
      </div>

      <template v-slot:append>
        <v-col class="d-flex justify-end">
          <div>
            <!-- <v-btn :icon="`ztIcon:${ztAliases.undo}`"></v-btn>
            <v-btn :icon="`ztIcon:${ztAliases.redo}`"></v-btn>
            <v-btn :icon="`ztIcon:${ztAliases.message}`"></v-btn> -->
            <v-tooltip text="Run All" location="bottom" color="primary">
              <template v-slot:activator="{ props }">
                <v-btn
                  v-if="$devMode && !isAppRoute"
                  :icon="`ztIcon:${ztAliases.play}`"
                  v-bind="props"
                  variant="flat"
                  ripple
                  color="bluegrey-darken-4"
                  @click="runCode('')"
                >
                </v-btn>
              </template>
            </v-tooltip>
            <v-menu
              v-if="$devMode && !isAppRoute"
              :close-on-content-click="false"
            >
              <template v-slot:activator="{ props }">
                <v-btn
                  :icon="`ztIcon:${ztAliases.settings}`"
                  v-bind="props"
                ></v-btn>
              </template>
              <v-list bg-color="bluegrey-darken-4">
                <v-list-item>
                  <template v-slot:prepend>
                    <v-switch v-model="reactiveMode"></v-switch>
                  </template>
                  <v-list-item-title>Reactive Mode</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
            <v-btn v-if="$devMode && !isAppRoute" :icon="`ztIcon:${ztAliases.message}`" @click="showAllComments"></v-btn>
            <ShareComponent v-if="$devMode && !isAppRoute" />
          </div>
        </v-col>
      </template>
    </v-app-bar>
    <v-navigation-drawer
      v-if="$devMode && !isMobile && !isAppRoute"
      :rail="true"
      color="bluegrey-darken-4"
      style="padding-top: 12px; padding-bottom: 12px"
    >
      <template #append>
        <v-list-item>
          <CopilotComponent v-if="$devMode && !isAppRoute" />
        </v-list-item>
        <v-list-item>
          <v-btn
            color="bluegrey-darken-4"
            icon="mdi-folder-multiple"
            @click="drawer = true"
            class="text-bluegrey"
          />
        </v-list-item>
        <v-list-item>
          <PackageComponent
            v-if="$devMode && !isAppRoute"
            :dependencies="dependencies"
            :dependencyOutput="dependencyOutput"
            @updateDependencies="updateDependencies"
          />
        </v-list-item>
      </template>
    </v-navigation-drawer>
    <SidebarComponent
      :drawer="drawer"
      :items="items"
      :tree="tree"
      :fileIcon="fileIcon"
      :isMobile="isMobile"
      :isAppRoute="isAppRoute"
      @update:drawer="updateDrawer"
      @update:items="updateItems"
      @handleFileChange="handleFileChange"
      style="padding-top: 12px; padding-bottom: 12px"
    />
    <v-main :scrollable="false" class="w-100 mx-auto">
      <v-container v-if="errorMessage">
        <v-alert type="error">
          {{ errorMessage }}
        </v-alert>
      </v-container>
      <v-container v-if="socketsDisconnected">
        <v-alert type="error">
          Connection to the server has been lost. Please refresh the page.
        </v-alert>
      </v-container>
      <div :class="['content', 'px-8', 'd-flex', 'justify-center']">
        <div class="content__cells flex-grow-1" transition="slide-x-transition">
          <CodeCellManager 
            :notebook="notebook"
            :completions="completions"
            @runCode="runCode"
            @saveCell="saveCell"
            @componentValueChange="componentValueChange"
            @deleteCell="deleteCell"
            @createCell="createCodeCell"
            @copilotCompletion="copilotCompletion"
            @updateTimers="startTimerComponents"
          />
        </div>
        <div
          :class="[
            'content__comments',
            {
              'content__comments--show': showComments,
            },
          ]"
        >
          <Comments />
        </div>
      </div>
    </v-main>
    <v-footer
      app
      class="footer bg-bluegrey-darken-4 text-bluegrey"
      v-if="!isMobile"
    >
      <div class="footer__left-container">
        <span>
          <span>Python {{ pythonVersion }}</span>
        </span>
        <v-icon class="dot-divider" :icon="`ztIcon:${ztAliases.dot}`" />
        <span>Zero-True {{ ztVersion }}</span>
        <v-icon class="dot-divider" :icon="`ztIcon:${ztAliases.dot}`" />
        <span>{{ cellLength }} cells</span>
      </div>
      <div class="footer__right-container">
        <div class="footer__queue-length-wrapper" v-if="isCodeRunning">
          <v-progress-circular
            indeterminate
            color="bluegrey"
            size="17"
            class="footer__code-running-loader"
            id="codeRunProgress"
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
            <v-menu activator="parent">
              <v-list class="footer__queue-list">
                <v-list-item
                  v-for="(item, i) in runningQueue"
                  :key="i"
                  class="footer__queue-list-item"
                >
                  <span class="text-bluegrey">Python #2</span>
                  <template v-slot:append>
                    <v-icon icon="$done" color="success" />
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
          <div v-if="isCodeRunning" class="footer__status">
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
import { nextTick } from "vue";
import { useRoute } from "vue-router";
import { Request, CodeRequest } from "./types/request";
import { ComponentRequest } from "./types/component_request";
import { DeleteRequest } from "./types/delete_request";
import { SaveRequest } from "./types/save_request";
import { CreateRequest, Celltype } from "./types/create_request";
import { ClearRequest } from "./types/clear_request";
import { NotebookNameRequest } from "./types/notebook_name_request";
import { Notebook, CodeCell, Layout, ZTComponent } from "./types/notebook";
import { Dependencies } from "./types/notebook_response";
import { DependencyOutput } from "./static-types/dependency_ouput";
import CodeComponent from "@/components/CodeComponent.vue";
import MarkdownComponent from "@/components/MarkdownComponent.vue";
import EditorComponent from "@/components/EditorComponent.vue";
import SQLComponent from "@/components/SQLComponent.vue";
import PackageComponent from "@/components/PackageComponent.vue";
import Comments from "@/components/comments/Comments.vue";
import CodeCellManager from "./components/CodeCellManager.vue";
import CopilotComponent from "./components/CopilotComponent.vue";
import ShareComponent from "./components/ShareComponent.vue";
import type { VTextField } from "vuetify/lib/components/index.mjs";
import { ztAliases } from "@/iconsets/ztIcon";
import { Timer } from "@/timer";
import { globalState } from "@/global_vars";
import { DependencyRequest } from "./types/dependency_request";
import SidebarComponent from "@/components/FileExplorer.vue";
import { WebSocketManager } from "@/websocket_manager";

import { useCommentsStore } from '@/stores/comments'

export default {
  components: {
    CodeComponent,
    MarkdownComponent,
    EditorComponent,
    SQLComponent,
    PackageComponent,
    CodeCellManager,
    CopilotComponent,
    ShareComponent,
    SidebarComponent,
    Comments,
  },

  data() {
    return {
      editingProjectName: false,
      errorMessage: "" as string,
      notebook: {} as Notebook,
      notebookName: "",
      notebookEditName: "",
      dependencies: {} as Dependencies,
      completions: {} as { [key: string]: any[] },
      ws_url: "",
      pythonVersion: "",
      ztVersion: "",
      notebook_socket: null as WebSocketManager | null,
      save_socket: null as WebSocketManager | null,
      run_socket: null as WebSocketManager | null,
      stop_socket: null as WebSocketManager | null,
      dependency_socket: null as WebSocketManager | null,
      timer: 0,
      startTime: 0,
      timerInterval: null as ReturnType<typeof setInterval> | null,
      isCodeRunning: false,
      requestQueue: [] as any[],
      componentChangeQueue: [] as any[],
      drawer: false,
      files: [] as any[],
      tree: [],
      items: [] as any[],
      openFolders: [],
      reactiveMode: true,
      showComments: false,
      concatenatedCodeCache: {
        lastCellId: "" as string,
        code: "" as string,
        followingCode: "" as string,
        length: 0 as number,
      },
      dependencyOutput: { output: "", isLoading: false } as DependencyOutput,
      ztAliases,
    };
  },

  setup() {
    const commentsStore  = useCommentsStore()
    const { showAllComments } = commentsStore;
    const { showComments } = storeToRefs(commentsStore);
    return {
      showComments,
      showAllComments,
    }
  },

  beforeMount() {
    window.addEventListener("beforeunload", this.clearState);
    window.addEventListener("unload", this.clearState);
  },

  beforeUnmount() {
    window.removeEventListener("beforeunload", this.clearState);
    window.removeEventListener("unload", this.clearState);
  },

  async mounted() {
    await this.get_env_data();
    await this.connectSockets();
    this.isCodeRunning = true;
    this.startTimer();
    this.notebook_socket!.send(JSON.stringify({ message: "" }));
  },

  computed: {
    isAppRoute() {
      const route = useRoute();
      return route.path === "/app";
    },
    isMobile() {
      return this.$vuetify.display.mobile;
    },
    cellLength() {
      return this.notebook.cells ? Object.keys(this.notebook.cells).length : 0;
    },
    runningQueue() {
      return this.$devMode ? this.requestQueue : this.componentChangeQueue;
    },
    queueLength() {
      return this.runningQueue.length;
    },
    socketsDisconnected() {
      return globalState.connection_lost;
    },
  },

  methods: {
    async connectSockets() {
      this.notebook_socket = new WebSocketManager(this.ws_url + "ws/notebook", {
        onMessage: (message: any) => this.notebookOnMessage(message),
      });
      this.run_socket = new WebSocketManager(
        this.$devMode
          ? this.ws_url + "ws/run_code"
          : this.ws_url + "ws/component_run",
        {
          onMessage: (message: any) => this.runOnMessage(message),
        }
      );
      this.stop_socket = new WebSocketManager(
        this.ws_url + "ws/stop_execution"
      );
      await this.notebook_socket.initializeSocket();
      await this.run_socket.initializeSocket();
      await this.stop_socket.initializeSocket();
      if (this.$devMode) {
        this.save_socket = new WebSocketManager(this.ws_url + "ws/save_text", {
          onMessage: (message: any) => this.saveOnMessage(message),
        });
        this.dependency_socket = new WebSocketManager(
          this.ws_url + "ws/dependency_update",
          {
            onMessage: (message: any) => this.dependencyOnMessage(message),
          }
        );
        await this.save_socket.initializeSocket();
        await this.dependency_socket.initializeSocket();
      }
    },

    toggleProjectName() {
      this.editingProjectName = !this.editingProjectName;
      if (this.editingProjectName) {
        this.notebookEditName = this.notebookName;
        nextTick(() => {
          (this.$refs.projectNameField as VTextField).focus();
        });
      }
    },
    async saveProjectName() {
      if (this.editingProjectName) {
        const notebookNameRequest: NotebookNameRequest = {
          notebookName: this.notebookEditName,
        };
        await axios.post(
          import.meta.env.VITE_BACKEND_URL + "api/notebook_name_update",
          notebookNameRequest
        );
        this.notebookName = this.notebookEditName;
        document.title = this.notebookName;
        this.editingProjectName = false;
      }
    },

    startTimer() {
      this.startTime = Date.now();
      this.timer = 0;

      this.timerInterval = setInterval(() => {
        const currentTime = Date.now();
        this.timer = currentTime - this.startTime;
      }, 99);
    },

    stopTimer() {
      if (this.timerInterval) {
        clearInterval(this.timerInterval);
        this.timerInterval = null;
      }
    },

    async get_env_data() {
      const response = await axios.get(
        import.meta.env.VITE_BACKEND_URL + "env_data"
      );
      const envData = response.data;
      this.ws_url = envData.ws_url || import.meta.env.VITE_WS_URL;
      this.pythonVersion = envData.python_version;
      this.ztVersion = envData.zt_version;
    },

    updateDrawer(value: boolean) {
      this.drawer = value;
    },

    updateItems(newItems: any[]) {
      this.items = newItems;
    },

    handleFileChange(componentId: string, event: Event) {
      const file = (event.target as HTMLInputElement).files;
      if (file && file.length > 0) {
        const formData = new FormData();
        formData.append("file", file[0]);
        axios
          .post(
            `${import.meta.env.VITE_BACKEND_URL}api/upload_file`,
            formData,
            {
              headers: { "Content-Type": "multipart/form-data" },
            }
          )
          .then((response) => console.log("File processed", response.data))
          .catch((error) =>
            console.error("Error processing file:", error.response)
          ); // Directly pass the file to `runCode`
      } else {
        console.error("No file selected");
      }
    },

    fileIcon(extension: string) {
      switch (extension) {
        case "html":
          return "mdi:mdi-language-html5";
        case "js":
          return "mdi:mdi-nodejs";
        case "json":
          return "mdi:mdi-code-json";
        case "md":
          return "mdi:mdi-language-markdown";
        case "pdf":
          return "mdi:mdi-file-pdf-box";
        case "png":
          return "mdi:mdi-file-image";
        case "txt":
          return "mdi:mdi-file-document-outline";
        case "xls":
          return "mdi:mdi-file-excel";
        case "folder":
          return "mdi:mdi-folder";
        default:
          return "mdi:mdi-file";
      }
    },

    async runCode(originId: string) {
      const cellRequests: CodeRequest[] = [];
      const requestComponents: { [key: string]: any } = {};
      for (let key in this.notebook.cells) {
        const cellRequest: CodeRequest = {
          id: key,
          code: this.notebook.cells[key].code,
          variable_name: this.notebook.cells[key].variable_name || "",
          nonReactive: this.notebook.cells[key].nonReactive as boolean,
          showTable: this.notebook.cells[key].showTable as boolean,
          cellType: this.notebook.cells[key].cellType,
        };
        for (const c of this.notebook.cells[key].components) {
          if (c.component === "v-data-table") {
            requestComponents[c.id] = "";
          } else {
            requestComponents[c.id] = c.value;
          }
        }
        cellRequests.push(cellRequest);
      }
      const request: Request = {
        originId: originId,
        reactiveMode: this.reactiveMode,
        cells: cellRequests,
        components: requestComponents,
      };

      if (this.isCodeRunning) {
        const existingRequestIndex = this.requestQueue.findIndex(
          (req) => req.originId === originId
        );
        if (existingRequestIndex !== -1) {
          this.requestQueue[existingRequestIndex] = request;
        } else {
          this.requestQueue.push(request);
        }
        return;
      }

      this.sendRunCodeRequest(request);
    },

    sendRunCodeRequest(request: Request) {
      this.isCodeRunning = true;
      this.startTimer();
      this.run_socket!.send(JSON.stringify(request));
    },

    notebookOnMessage(event: any) {
      const response = JSON.parse(event.data);
      if (response.notebook_name) {
        this.notebookName = response.notebook_name;
        document.title = this.notebookName;
      } else if (response.cell_id) {
        if (response.clear_output) {
          this.notebook.cells[response.cell_id].output = "";
        } else {
          this.notebook.cells[response.cell_id].output = this.notebook.cells[
            response.cell_id
          ].output.concat(response.output);
        }
      } else if (response.env_stale) {
        this.errorMessage =
          "Some dependencies are not installed in the current environment. Open dependency manager to install missing dependencies";
      } else if (response.complete) {
        this.isCodeRunning = false;
        this.stopTimer();
      } else {
        const cell_response =
          typeof response === "string" ? JSON.parse(response) : response;
        if (cell_response.notebook) {
          this.notebook = cell_response.notebook;
          for (let cell_id in this.notebook.cells) {
            if (this.notebook.cells[cell_id].cellType === "code") {
              this.completions[cell_id] = [];
            }
          }
          this.dependencies = cell_response.dependencies;
        } else {
          if (this.notebook.cells && this.notebook.cells[cell_response.id]) {
            this.notebook.cells[cell_response.id].components =
              cell_response.components;
            this.notebook.cells[cell_response.id].layout =
              cell_response.layout as Layout | undefined;
          }
        }
      }
    },

    runOnMessage(event: any) {
      const response = JSON.parse(event.data);
      if (!this.$devMode && response.refresh) {
        this.notebookRefresh();
      } else if (response.cell_id) {
        if (response.clear_output) {
          this.notebook.cells[response.cell_id].output = "";
        } else {
          this.notebook.cells[response.cell_id].output = this.notebook.cells[
            response.cell_id
          ].output.concat(response.output);
        }
      } else if (response.complete) {
        this.isCodeRunning = false;
        this.stopTimer();
        if (this.$devMode && this.requestQueue.length > 0) {
          const currentRequest = this.requestQueue.shift() || {};
          this.sendRunCodeRequest(currentRequest);
        } else if (!this.$devMode && this.componentChangeQueue.length > 0) {
          const componentChangeRequest =
            this.componentChangeQueue.shift() || {};
          const componentRequest: ComponentRequest = {
            originId: componentChangeRequest.originId,
            components: componentChangeRequest.components,
            userId: componentChangeRequest.userId,
          };
          this.sendComponentRequest(componentRequest);
        }
      } else {
        const components_response = JSON.parse(response);
        this.notebook.cells[components_response.id].components =
          components_response.components;
        this.notebook.cells[components_response.id].layout =
          components_response.layout as Layout | undefined;
      }
    },

    saveOnMessage(event: any) {
      try {
        const data = JSON.parse(event.data);
        // Assuming data is an array of completion objects
        this.completions[data.cell_id] = Array.isArray(data.completions)
          ? data.completions
          : [];
      } catch (error) {
        console.error("Error parsing server message:", error);
      }
    },

    dependencyOnMessage(event: any) {
      try {
        const data = JSON.parse(event.data);
        if (data.output) {
          this.dependencyOutput.output = this.dependencyOutput.output.concat(
            data.output
          );
        } else {
          this.dependencies = JSON.parse(data);
          this.dependencyOutput.isLoading = false;
        }
        this.errorMessage = "";
      } catch (error) {
        console.error("Error parsing server message:", error);
      }
    },

    async componentValueChange(
      originId: string,
      componentId: string,
      newValue: any
    ) {
      // Updating the component's value in the notebook
      const requestComponents: { [key: string]: any } = {};
      for (let key in this.notebook.cells) {
        for (const c of this.notebook.cells[key].components) {
          if (c.component === "v-data-table") {
            requestComponents[c.id] = "";
          } else {
            requestComponents[c.id] = c.value;
          }
        }
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
        const existingRequestIndex = this.componentChangeQueue.findIndex(
          (req) => req.componentId === componentId
        );
        if (existingRequestIndex !== -1) {
          this.componentChangeQueue[existingRequestIndex] =
            componentChangeRequest;
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

      this.sendComponentRequest(componentRequest);
    },

    async sendComponentRequest(componentRequest: ComponentRequest) {
      this.isCodeRunning = true;
      this.startTimer();
      this.run_socket!.send(JSON.stringify(componentRequest));
    },

    async notebookRefresh() {
      //TODO: Fix this
      this.isCodeRunning = true;
      this.startTimer();
      this.notebook_socket!.send(JSON.stringify({ message: "start" }));
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
      const cellRequest: CreateRequest = {
        cellType: cellType.toLowerCase() as Celltype,
        position_key: position_key,
      };
      const response = await axios.post(
        import.meta.env.VITE_BACKEND_URL + "api/create_cell",
        cellRequest
      );
      const cell: CodeCell = response.data;
      let cells: Record<string, CodeCell> = {};
      if (!position_key) {
        cells[cell.id] = cell;
      }
      for (let key in this.notebook.cells) {
        cells[key] = this.notebook.cells[key];
        if (position_key === key) {
          cells[cell.id] = cell;
        }
      }
      if (cell.cellType === "code") {
        this.completions[cell.id] = [];
      }
      this.notebook.cells = cells;
    },

    async deleteCell(cellId: string) {
      const deleteRequest: DeleteRequest = { cellId: cellId };
      await axios.post(
        import.meta.env.VITE_BACKEND_URL + "api/delete_cell",
        deleteRequest
      );
      if (this.notebook.cells[cellId].cellType === "code") {
        delete this.completions[cellId];
      }
      delete this.notebook.cells[cellId];
    },

    async saveCell(cellId: string, text: string, line: string, column: string) {
      if (this.notebook.cells[cellId].cellType === "code") {
        if (this.concatenatedCodeCache.lastCellId !== cellId) {
          let concatenatedCode = "";
          let followingCode = "";
          let length = 0;
          let prevCode = true;
          for (let key in this.notebook.cells) {
            if (key === cellId) {
              prevCode = false;
              continue;
            }
            if (this.notebook.cells[key].cellType === "code") {
              if (prevCode) {
                concatenatedCode += this.notebook.cells[key].code + "\n";
                length +=
                  this.notebook.cells[key].code.split(/\r\n|\r|\n/).length;
              } else {
                followingCode += this.notebook.cells[key].code + "\n";
              }
            }
          }

          // Update the cache
          this.concatenatedCodeCache = {
            lastCellId: cellId,
            code: concatenatedCode,
            followingCode: followingCode,
            length: length,
          };
        }
      }
      // The rest of the saveCell method remains unchanged
      const saveRequest: SaveRequest = {
        id: cellId,
        text: text, // Use the concatenated code from previous cells
        cellType: this.notebook.cells[cellId].cellType,
        line: this.concatenatedCodeCache.length + line,
        column: column,
        code_w_context:
          this.concatenatedCodeCache.code +
          text +
          this.concatenatedCodeCache.followingCode,
      };
      this.save_socket!.send(JSON.stringify(saveRequest));
    },

    async copilotCompletion(
      cellId: string,
      line: string,
      column: string,
      callback: any
    ) {
      if (this.concatenatedCodeCache.lastCellId !== cellId) {
        let concatenatedCode = "";
        let followingCode = "";
        let length = 0;
        let prevCode = true;
        for (let key in this.notebook.cells) {
          if (key === cellId) {
            prevCode = false;
            continue;
          }
          if (this.notebook.cells[key].cellType === "code") {
            if (prevCode) {
              concatenatedCode += this.notebook.cells[key].code + "\n";
              length +=
                this.notebook.cells[key].code.split(/\r\n|\r|\n/).length;
            } else {
              followingCode += this.notebook.cells[key].code + "\n";
            }
          }
        }

        // Update the cache
        this.concatenatedCodeCache = {
          lastCellId: cellId,
          code: concatenatedCode,
          followingCode: followingCode,
          length: length,
        };
      }
      const response = await axios.post(
        import.meta.env.VITE_BACKEND_URL + "copilot/get_completions",
        {
          doc: {
            version: 1,
            uri: "file:///notebook.ztnb",
            position: {
              line: this.concatenatedCodeCache.length + line,
              character: column,
            },
          },
        }
      );
      callback(response);
    },

    async stopCodeExecution() {
      if (this.$devMode) {
        this.requestQueue = [];
        this.stop_socket!.send(JSON.stringify({ userId: "" }));
      } else {
        this.componentChangeQueue = [];
        this.stop_socket!.send(
          JSON.stringify({ userId: this.notebook.userId })
        );
      }
      for (let key in this.notebook.cells) {
        for (const c of this.notebook.cells[key].components) {
          if (c.component === "v-btn" || c.component === "v-timer") {
            c.value = false;
          }
        }
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

    async updateDependencies(dependencies: Dependencies) {
      this.dependencyOutput.output = "";
      const request: DependencyRequest = { dependencies: dependencies };
      this.dependency_socket!.send(JSON.stringify(request));
    },

    startTimerComponents(originId: string, timers: ZTComponent[]) {
      if (!globalState.timers[originId]) {
        globalState.timers[originId] = {};
      } else {
        for (const timer in globalState.timers[originId]) {
          globalState.timers[originId][timer].stop();
          delete globalState.timers[originId][timer];
        }
      }
      for (const timer of timers) {
        this.startTimerComponent(originId, timer.id, timer.interval as number);
      }
    },

    startTimerComponent(originId: string, timerId: string, interval: number) {
      const startTimer = () => {
        const timer = new Timer(interval);
        globalState.timers[originId][timerId] = timer;
        timer.start(startTimer);
        this.notebook.cells[originId].components.find(
          (c: ZTComponent) => c.id === timerId
        )!.value = true;
        if (this.$devMode) {
          this.runCode(originId);
        } else {
          this.componentValueChange(originId, timerId, true);
        }
      };

      if (!globalState.timers[originId][timerId]) {
        const timer = new Timer(interval);
        globalState.timers[originId][timerId] = timer;
        timer.start(startTimer);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/styles/mixins.scss";
.zt-app-bar {
  padding-top: 6px;
  padding-bottom: 6px;
}

.logo-btn {
  & :deep(.v-icon) {
    width: 1.5em;
    height: 1.5em;
  }
}

.cm-editor {
  height: auto !important;
}

.click-edit {
  max-width: 200px;
  width: 100%;
  &__name {
    font-weight: normal;
    cursor: text;
  }
  &__show-text,
  &__edit-field-wrapper {
    display: flex;
    align-items: center;
  }

  &__name:hover {
    padding-left: 3px;
    padding-right: 3px;
    cursor: text;
    border: 1px solid #294455;
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
    max-width: 450px;
  }

  @include xl {
    max-width: 600px;
  }
}
.content {
  &__comments {
    width: 0;
    transition: width .15s ease;
    &--show {
      width: 380px;
    }
  }
}
.footer {
  display: flex;
  justify-content: space-between;
  flex-direction: column;
  padding: 4px 16px;
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
    height: 34px;
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
