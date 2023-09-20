<template>
    <v-card flat>
        <ace-editor
            v-model:value="cellData.code"
            ref="editor"
            class="editor"
            theme="dracula"
            lang="markdown"
            :options="{
                showPrintMargin: false,
                enableBasicAutocompletion: true,
                enableSnippets: true,
                enableLiveAutocompletion: true
            }"
        >
        </ace-editor>
        <Markdown :source="cellData.code" />
        <v-toolbar>
            <v-spacer/>
            <v-btn small color="primary" @click="deleteCell">Delete Cell</v-btn>
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
        deleteCell(){
            this.$emit('deleteCell', this.cellData.id);
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