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
    <template v-for="(row, rowIndex) in cellData.layout.rows" :key="row.id">
      <v-row>
        <!-- Loop through columns in each row -->
        <template v-for="(column, columnIndex) in row.columns" :key="column.id">
          <v-col :cols="12 / row.columns.length">
            <!-- Loop through component IDs in each column -->
            <template v-for="(componentId, componentIndex) in column.components" :key="componentId">
              <!-- Render the component -->
              <component 
                :is="findComponentById(componentId).component" 
                v-bind="findComponentById(componentId)"
                v-model="findComponentById(componentId).value"
                @[findComponentById(componentId).triggerEvent]="runCode"
              >
                <template v-if="findComponentById(componentId).component === 'v-data-table'" v-slot:items="props">
                    <td v-for="(value, key) in props.item" :key="key">{{ value }}</td>
                </template>
              </component>
            </template>
          </v-col>
        </template>
      </v-row>
    </template>

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
      const placedComponentIds = this.cellData.layout.rows.flatMap(row =>
        row.columns.flatMap(column => column.components)
      );
      return this.cellData.components.filter(
        comp => !placedComponentIds.includes(comp.id)
      );
    },
  },
  methods: {
    runCode() {
      this.$emit('runCode', this.cellData.id);
    },
    deleteCell() {
      this.$emit('deleteCell', this.cellData.id);
    },
    findComponentById(id: string) {
      return this.cellData.components.find(comp => comp.id === id);
    },
  },
}
</script>
