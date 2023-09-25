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
import { VSlider, VTextField, VTextarea, VRangeSlider, VSelect, VCombobox, VBtn, VImg} from 'vuetify/lib/components/index.mjs';
import VText from './TextComponent.vue';
import { CodeCell,ZTComponent } from '@/types/notebook';


export default {
    components: {
        'ace-editor': VAceEditor,
        'v-slider': VSlider,
        'v-text-field': VTextField,
        'v-number-field': VTextField,
        'v-textarea': VTextarea,
        'v-range-slider': VRangeSlider,
        'v-select':VSelect,
        'v-combobox':VCombobox,
        'v-btn': VBtn,
        'v-img': VImg,
        'v-text': VText,
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
            const rows: Record<number, ZTComponent[][]> = {};
            const bottomRow: ZTComponent[] = [];  // For components without a row or column
            
            for (const component of this.cellData.components) {
            if (component.row !== null && component.row !== undefined &&
                component.column !== null && component.column !== undefined) {
                const row = component.row;
                if (!rows[row]) rows[row] = [];
                const column = component.column;
                
                // Initialize the column as an array if it doesn't exist
                if (!rows[row][column]) rows[row][column] = [];
                
                // Append the component to the existing column
                rows[row][column].push(component);
                
            } else {
                // Place components without a row or column at the bottom
                bottomRow.push(component);
            }
            }
            
            // Sort by row number and add the bottom row at the end
            const sortedRowNumbers = Object.keys(rows).sort((a, b) => Number(a) - Number(b));
            const sortedRows = sortedRowNumbers.map(rowNum => {
            const row = rows[Number(rowNum)];
            return row.reduce((acc: ZTComponent[], col: ZTComponent[] = []) => acc.concat(col), []);
            });
            
            sortedRows.push(bottomRow);  // Add the bottom row
            
            return sortedRows;
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
