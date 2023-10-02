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
      <v-spacer />
      <v-btn variant="flat" color="error" @click="deleteCell">Delete Cell</v-btn>
    </v-toolbar>

    <row-component v-for="(row, rowIndex) in cellData.layout?.rows" 
      :key="rowIndex"
      :row-data="row"
      :components="cellData.components"
      @runCode="runCode"/>
    <!-- Render unplaced components at the bottom -->
    <v-row>
      <v-col v-for="component in unplacedComponents" :key="component.id">
        <component
          :is="component.component"
          v-bind="component"
          v-model="component.value"
          @[component.triggerEvent]="runCode"
        ></component>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <div class="text-p">{{cellData.output}}</div>
      </v-col>
    </v-row>
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
  import { CodeCell, ZTLayout } from '@/types/notebook'
  import RowComponent from '@/components/RowComponent.vue';
  
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
      'row-component': RowComponent,
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
        const findPlacedIds = (rows: any[]): string[] => {
          let ids: string[] = [];
          for (const row of rows) {
            for (const column of row?.columns ?? []) {
              for (const component of column?.components ?? []) {
                if (typeof component === 'string') {
                  // It's an ID of a regular component
                  ids.push(component);
                } else if (component && component.columns) {
                  // It's a nested row, go deeper
                  ids = ids.concat(findPlacedIds([component]));
                }
              }
            }
          }
          return ids;
        };

        const placedComponentIds = findPlacedIds((this.cellData.layout as ZTLayout)?.rows ?? []);
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
      }
    },
  }
  </script>
  