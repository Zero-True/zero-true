<template>
    <v-card flat color="bluegrey">
        <ace-editor
            v-if="$devMode"
            v-model:value="cellData.code"
            ref="editor"
            class="editor"
            theme="dracula"
            lang="markdown"
            :options="{
                showPrintMargin: false,
                enableBasicAutocompletion: true,
                enableSnippets: true,
                enableLiveAutocompletion: true,
                autoScrollEditorIntoView: true,
                minLines: 5,
                maxLines: Infinity
            }"
        />
        <Markdown :source="cellData.code" />
        <v-toolbar v-if="$devMode" color="bluegrey">
            <v-btn variant="flat" color="primary" @click="saveCell">Save</v-btn>
            <v-spacer/>
            <v-btn variant="flat" color="error" @click="deleteCell">Delete Cell</v-btn>
        </v-toolbar>
    </v-card>
</template>

<script lang="ts">
import type { PropType } from 'vue'
import Markdown from 'vue3-markdown-it';
import { VAceEditor } from 'vue3-ace-editor';
import 'ace-builds/src-noconflict/mode-markdown';
import 'ace-builds/src-noconflict/snippets/markdown';
import 'ace-builds/src-noconflict/ext-language_tools';
import 'ace-builds/src-noconflict/theme-dracula';
import { CodeCell } from '@/types/notebook';


export default {
    components: {
        'ace-editor': VAceEditor,
        Markdown
    },
    props: {
        cellData: {
            type: Object as PropType<CodeCell>,
            required: true,
        },
    },
    methods: {
        saveCell(){
            this.$emit('saveCell', this.cellData.id);
        },
        deleteCell(){
            this.$emit('deleteCell', this.cellData.id);
        }
    },
}
</script>