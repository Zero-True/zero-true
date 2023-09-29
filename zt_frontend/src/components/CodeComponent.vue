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
      <div v-for="(row, rowIndex) in renderLayout(cellData.layout)" :key="rowIndex">
  <v-row>
    <v-col v-for="(col, colIndex) in row?.columns ?? []" :key="colIndex" :cols="12 / (row?.columns?.length ?? 1)">
      <div v-for="(component, componentIndex) in col.components" :key="componentIndex">
        <template v-if="component.type === 'nested'">
          <!-- Recursive rendering for nested rows -->
          <div v-for="(nestedRow, nestedRowIndex) in component.layout" :key="nestedRowIndex">
            <v-row>
              <v-col v-for="(nestedCol, nestedColIndex) in nestedRow?.columns ?? []" :key="nestedColIndex" :cols="12 / (nestedRow?.columns?.length ?? 1)">
                <div v-for="(nestedComponent, nestedComponentIndex) in nestedCol.components" :key="nestedComponentIndex">
                  <!-- Render nested components here -->
                  <component
                    :is="nestedComponent.component"
                    v-bind="nestedComponent"
                    v-model="nestedComponent.value"
                    @[nestedComponent.triggerEvent]="runCode"
                  ></component>
                </div>
              </v-col>
            </v-row>
          </div>
        </template>
        <template v-else>
          <!-- Regular component rendering -->
          <component
            :is="component.component"
            v-bind="component"
            v-model="component.value"
            @[component.triggerEvent]="runCode"
          ></component>
        </template>
      </div>
    </v-col>
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
  import { CodeCell, ZTLayout } from '@/types/notebook';
  
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
      },
      findComponentById(id: string) {
        return this.cellData.components.find(comp => comp.id === id);
      },
      renderLayout(layout: any) {
        return layout.rows.map((row: any) => {
            return {
            type: 'row',
            id: row.id,
            columns: row.columns.map((column: any) => {
                return {
                type: 'column',
                id: column.id,
                components: column.components.map((componentOrNestedRow: any) => {
                    if (typeof componentOrNestedRow === 'string') {
                    return this.findComponentById(componentOrNestedRow);
                    } else if (componentOrNestedRow.id && componentOrNestedRow.columns) {
                    return {
                        type: 'nested',
                        layout: this.renderLayout({ rows: [componentOrNestedRow] })
                    };
                    }
                })
                };
            })
            };
        });
        },
    },
  }
  </script>
  