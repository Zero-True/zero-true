<template>
    <v-card flat color="bluegrey">
        <v-row  v-if="$devMode" no-gutters class="py-1 toolbar-bg">
        <v-col :cols="11">
        <span class="py-0 px-2">.md</span>

            <!-- Placeholder for future content or can be empty -->
        </v-col>
        <v-col :cols="1" class="d-flex justify-end align-center py-0">
            <v-icon small class="mx-1" color="primary" @click="saveCell">
                mdi-content-save
            </v-icon>
            <v-icon small class="mx-1" color="error" @click="deleteCell">
                mdi-delete
            </v-icon>
        </v-col>
        </v-row>
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