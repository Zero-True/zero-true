<template>
<v-card flat>
    <ace-editor
        v-model:value="cellData.code"
        ref="editor"
        class="editor"
        theme="dracula"
        lang="python"
        :options="{
            showPrintMargin: false,
            enableBasicAutocompletion: true,
            enableSnippets: true,
            enableLiveAutocompletion: true
        }"
    >
    </ace-editor>
    <v-toolbar>
        <v-btn color="primary" @click="runCode">Run</v-btn>
        <v-spacer/>
        <v-btn small color="primary" @click="deleteCell">Delete Cell</v-btn>
    </v-toolbar>
    <!-- Render Components -->
    <v-row v-for="(row, rowIndex) in sortedRows" :key="'row-' + rowIndex" no-gutters>
      <v-col v-for="component in row" :key="component.id">
        <component :is="component.component" v-bind="component" v-model="component.value" @end="runCode"></component>
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
import { VSlider } from 'vuetify/lib/components/index.mjs';
import { CodeCell } from '@/types/notebook';


export default {
    components: {
        'ace-editor': VAceEditor,
        'v-slider': VSlider
    },
    props: {
        cellData: {
            type: Object as PropType<CodeCell>,
            required: true,
        },
    },
    methods: {
        runCode(){
            console.log(this.cellData)
            this.$emit('runCode', this.cellData.id);
        },
        handleValueChange(newValue:any, componentId: string){
            this.$emit('componentValueChange', componentId, newValue );
        },
        deleteCell(){
            this.$emit('deleteCell', this.cellData.id);
        }
    },
    computed: {
    sortedRows(): ZTComponent[][] {
      const rows: Record<number, ZTComponent[]> = {};
      for (const component of this.cellData.components) {
        const row = component.row !== null && component.row !== undefined ? component.row : -1;
        if (!rows[row]) rows[row] = [];
        const column = component.column !== null && component.column !== undefined ? component.column : rows[row].length;
        rows[row][column] = component;
      }
      // Sort by row number, placing the undefined row (-1) at the end
      const sortedRowNumbers = Object.keys(rows).sort((a, b) => Number(a) - Number(b));
      return sortedRowNumbers.map(rowNum => rows[Number(rowNum)].filter(Boolean));
    }
  },
}
</script>
    
<style scoped>
.editor {
    filter: none;
    height: 300px;
    width: 100%;
    margin-bottom: 20px;
}
</style>
