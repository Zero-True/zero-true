<template>
    <v-card flat color="bluegrey">
      <ace-editor
          v-model:value="cellData.code"
          ref="editor"
          class="editor"
          theme="dracula"
          lang="python"
          :options="editorOptions"
      />
      <v-toolbar color="bluegrey">
          <v-btn variant="flat" color="primary" @click="runCode">Run</v-btn>
          <v-spacer/>
          <v-btn variant="flat" color="error" @click="deleteCell">Delete Cell</v-btn>
      </v-toolbar>
  
      <!-- Loop through rows in the layout -->
  <!-- Loop through rows in the layout -->

  <div v-for="(row, rowIndex) in renderLayout(cellData.layout)" :key="rowIndex">
    <v-row>
      <div v-for="(col, colIndex) in row" :key="colIndex">
        <v-col :cols="col.length > 0 ? 6 : 12">
          <div v-for="(component, componentIndex) in col" :key="componentIndex">
            <!-- Here, use your logic to render the component, similar to what you had before -->
            <component 
              :is="component.component" 
              v-bind="component" 
              v-model="component.value" 
              @[component.triggerEvent]="runCode"
            >
              <!-- ... (other logic) ... -->
            </component>
          </div>
        </v-col>
      </div>
    </v-row>
  </div>

  
  
      <!-- Render unplaced components at the bottom -->
      <v-row>
        <v-col v-for="component in unplacedComponents" :key="component.id">
          <component :is="component.component" v-bind="component" v-model="component.value" @[component.triggerEvent]="runCode"></component>
        </v-col>
      </v-row>
  
      <div class="text-p">{{cellData.output}}</div>
    </v-card>
  </template>
  
  <script lang="ts">
  import type { PropType } from 'vue'
  import { VAceEditor } from 'vue3-ace-editor';
  import 'ace-builds/src-noconflict/mode-python';
  import 'ace-builds/src-noconflict/snippets/python';
  import 'ace-builds/src-noconflict/ext-language_tools';
  import 'ace-builds/src-noconflict/theme-dracula';
  import { VSlider, VTextField, VTextarea, VRangeSlider, VSelect, VCombobox, VBtn, VImg } from 'vuetify/lib/components/index.mjs';
  import { VDataTable } from "vuetify/labs/VDataTable";
  import { CodeCell, ZTComponent } from '@/types/notebook';
  
  export default {
    components: {
      'ace-editor': VAceEditor,
      'v-slider': VSlider,
      'v-text-field': VTextField,
      'v-number-field': VTextField,
      'v-textarea': VTextarea,
      'v-range-slider': VRangeSlider,
      'v-select': VSelect,
      'v-combobox': VCombobox,
      'v-btn': VBtn,
      'v-img': VImg,
      'v-data-table': VDataTable,
    },
    props: {
      cellData: {
        type: Object as PropType<CodeCell>,
        required: true,
      },
    },
  
    
    computed: {
      editorOptions() {
        return {
          showPrintMargin: false,
          enableBasicAutocompletion: true,
          enableSnippets: true,
          enableLiveAutocompletion: true,
          autoScrollEditorIntoView: true,
          minLines: 15,
          maxLines: Infinity,
        };
      },
      unplacedComponents() {
        const placedComponentIds = this.cellData.layout.rows.flatMap((row: { columns: any[]; }) =>
          row.columns.flatMap((column: { components: any; }) => column.components)
        );
        return this.cellData.components.filter(
          comp => !placedComponentIds.includes(comp.id)
        );
      },
    },
    methods: {
      runCode() {
        console.log(this.cellData.layout)
        this.$emit('runCode', this.cellData.id);
      },
      deleteCell() {
        this.$emit('deleteCell', this.cellData.id);
      },
      findComponentById(id: string) {
        return this.cellData.components.find(comp => comp.id === id);
      },
      renderLayout(layout: unknown) {
    const elements: any[] = [];
    layout.rows.forEach((row: { columns: any[]; }) => {
      const rowElement: any[][] = [];
      row.columns.forEach((column: { components: any[]; }) => {
        const colElement: (any[] | ZTComponent)[] = [];
        column.components.forEach((componentId: string) => {
          const component = this.findComponentById(componentId);
          if (component) {
            colElement.push(component);  // Directly pushing the component; you might need to modify this
          } else if (typeof componentId === 'object' && componentId.rows) {
            colElement.push(this.renderLayout(componentId));
          }
        });
        rowElement.push(colElement);
      });
      elements.push(rowElement);
    });
    return elements;
  }
    },
  }
  </script>
  