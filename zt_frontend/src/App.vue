<template>
  <v-app style="background-color: #040607">
    <v-app-bar app color="bluegrey">
      <v-btn size="x-large" variant="text" @click="navigateToApp">
        <v-icon start size="x-large" icon="custom:ZTIcon"></v-icon>
        Zero-True
      </v-btn>
      <v-spacer></v-spacer>
      <div v-if="isCodeRunning" class="d-flex align-center">
        <v-progress-circular
          indeterminate
          color="white"
          size="24"
        ></v-progress-circular>
        <v-chip class="ml-2" color="white" text-color="black">
          {{ timer }}ms
        </v-chip>
        <v-chip v-if="$devMode" class="ml-2" color="white" text-color="black">
          Queue Length: {{ requestQueue.length }}
        </v-chip>
        <v-chip v-else class="ml-2" color="white" text-color="black">
          Queue Length: {{ componentChangeQueue.length }}
        </v-chip>
      </div>
      <PackageComponent v-if="$devMode" :dependencies="dependencies"/>
    </v-app-bar>
    <v-main>
      <v-container>
        <v-menu transition="scale-transition">
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
        <component
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
import { Response } from "./types/response";
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
      timer: 0, // The timer value
      timerInterval: null as ReturnType<typeof setInterval> | null, // To hold the timer interval
      isCodeRunning: false,
      requestQueue: [] as string[],
      componentChangeQueue: [] as  any[],
      menu_items: [
          { title: 'Code' },
          { title: 'SQL' },
          { title: 'Markdown' },
          { title: 'Text' },
        ],
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

  async created() {
    const response = await axios.get(
      import.meta.env.VITE_BACKEND_URL + "api/notebook"
    );
    this.notebook = response.data.notebook;
    this.dependencies = response.data.dependencies;
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

    async runCode(originId: string) {
      this.requestQueue.push(originId);

      if (this.isCodeRunning) {
        return;
      }

      while (this.requestQueue.length > 0) {
        const currentOriginId = this.requestQueue.shift();
        if (!currentOriginId) continue;
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
            requestComponents[c.id] = c.value;
          }
          cellRequests.push(cellRequest);
        }
        const request: Request = {
          originId: originId,
          cells: cellRequests,
          components: requestComponents,
        };

        this.isCodeRunning = true;
        this.startTimer();
        const axiosResponse = await axios.post(
          import.meta.env.VITE_BACKEND_URL + "api/runcode",
          request
        );
        this.stopTimer();
        this.isCodeRunning = false;
        const response: Response = axiosResponse.data;
        for (const cellResponse of response.cells) {
          this.notebook.cells[cellResponse.id].components =
            cellResponse.components;
          this.notebook.cells[cellResponse.id].output = cellResponse.output;
          this.notebook.cells[cellResponse.id].layout = cellResponse.layout as
            | Layout
            | undefined;
        }
      }
    },

    async componentValueChange(originId: string, componentId: string, newValue: any) {
      // Updating the component's value in the notebook
      const requestComponents: { [key: string]: any } = {};
      for (let key in this.notebook.cells) {
        for (const c of this.notebook.cells[key].components) {
          requestComponents[c.id] = c.value;
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
      const existingRequestIndex = this.componentChangeQueue.findIndex(req => req.componentId === componentId);
      if (existingRequestIndex !== -1) {
        this.componentChangeQueue[existingRequestIndex] = componentChangeRequest;
      } else {
        this.componentChangeQueue.push(componentChangeRequest);
      }

      // If code is already running, exit the function to wait for the current execution to finish
      if (this.isCodeRunning) {
        return;
      }

      // Process the queue
      while (this.componentChangeQueue.length > 0) {
        const currentRequest = this.componentChangeQueue.shift();
        if (!currentRequest) continue;


        const componentRequest: ComponentRequest = {
          originId: currentRequest.originId,
          components: currentRequest.components,
          userId: currentRequest.userId,
        };

        this.isCodeRunning = true;
        this.startTimer();
        const axiosResponse = await axios.post(
          import.meta.env.VITE_BACKEND_URL + "api/component_run",
          componentRequest
        );
        this.stopTimer();
        this.isCodeRunning = false;
        const response: Response = axiosResponse.data;
        if (response.refresh) {
          const notebookResponse = await axios.get(
            import.meta.env.VITE_BACKEND_URL + "api/notebook"
          );
          this.notebook = notebookResponse.data.notebook;
          this.dependencies = notebookResponse.data.dependencies;
        } else {
          for (const cellResponse of response.cells) {
            this.notebook.cells[cellResponse.id].components = cellResponse.components;
            this.notebook.cells[cellResponse.id].output = cellResponse.output;
            this.notebook.cells[cellResponse.id].layout = cellResponse.layout as Layout | undefined;
          }
        }
      }
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
      this.notebook.cells = cells;
    },

    async deleteCell(cellId: string) {
      const deleteRequest: DeleteRequest = { cellId: cellId };
      await axios.post(
        import.meta.env.VITE_BACKEND_URL + "api/delete_cell",
        deleteRequest
      );
      delete this.notebook.cells[cellId];
    },

    async saveCell(cellId: string) {
      const saveRequest: SaveRequest = {
        id: cellId,
        text: this.notebook.cells[cellId].code,
      };
      await axios.post(
        import.meta.env.VITE_BACKEND_URL + "api/save_text",
        saveRequest
      );
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
.editor {
  background-color: #1b2f3c;
  filter: none;
  height: 300px;
  width: 100%;
  margin-bottom: 5px;
}
.editor .ace_gutter {
  background: #1b2f3c;
}
.editor .ace_active-line {
  background: #0e1b23 !important;
}
.editor .ace_gutter-active-line {
  background: #0e1b23 !important;
}
</style>
