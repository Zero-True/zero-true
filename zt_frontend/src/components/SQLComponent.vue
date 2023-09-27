<template>
    <v-card flat color="bluegrey">
        <v-text-field
            v-model="cellData.variable_name"
            label="Enter SQL variable name"
        />
        <ace-editor
            v-model:value="cellData.code"
            ref="editor"
            class="editor"
            theme="dracula"
            lang="sql"
            :options="{
                showPrintMargin: false,
                enableBasicAutocompletion: true,
                enableSnippets: true,
                enableLiveAutocompletion: true,
                autoScrollEditorIntoView: true,
                minLines: 15,
                maxLines: Infinity
            }"
        />
        <v-toolbar color="bluegrey">
            <v-btn variant="flat" color="primary" @click="runCode">Run</v-btn>
            <v-spacer/>
            <v-btn variant="flat" color="error" @click="deleteCell">Delete Cell</v-btn>
        </v-toolbar>
        <v-container v-for="component in cellData.components" :key="component.id">
            <component :is="component.component" v-bind="component" v-model="component.value">
                <template v-if="component.component === 'v-data-table'" v-slot:items="props">
                    <td v-for="(value, key) in props.item" :key="key">{{ value }}</td>
                </template>
            </component>
        </v-container>
        <div class="text-p">{{cellData.output}}</div>
    </v-card>
</template>

<script lang="ts">
import type { PropType } from 'vue'
import { VAceEditor } from 'vue3-ace-editor';
import { VDataTable } from "vuetify/labs/VDataTable"
import 'ace-builds/src-noconflict/mode-sql';
import 'ace-builds/src-noconflict/snippets/markdown';
import 'ace-builds/src-noconflict/ext-language_tools';
import 'ace-builds/src-noconflict/theme-dracula';
import { CodeCell } from '@/types/notebook';


export default {
    components: {
        'ace-editor': VAceEditor,
        'v-data-table': VDataTable
    },
    props: {
        cellData: {
            type: Object as PropType<CodeCell>,
            required: true,
        },
    },
    methods: {
        runCode(){
            this.$emit('runCode', this.cellData.id);
        },
        deleteCell(){
            this.$emit('deleteCell', this.cellData.id);
        }
    },
}
</script>