<template>
<v-row justify="center">
    <v-dialog v-model="updatingDependencies" persistent width="1024">
    <template v-slot:activator="{ props }">
        <v-btn color="primary" v-bind="props"> Dependencies </v-btn>
    </template>
    <v-card>
        <v-card-title>
        <span class="text-h5">Add Dependencies</span>
        </v-card-title>
        <ace-editor
            v-model:value="dependencies.value"
            ref="editor"
            class="editor"
            theme="dracula"
            lang="text"
            :options="editorOptions"
            />
        <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
            color="blue-darken-1"
            variant="text"
            @click="updatingDependencies = false"
        >
            Close
        </v-btn>
        <v-btn
            color="blue-darken-1"
            variant="text"
            @click="updateDependencies"
        >
            Update
        </v-btn>
        </v-card-actions>
    </v-card>
    </v-dialog>
</v-row>
</template>

<script lang="ts">
import type { PropType } from "vue";
import { VAceEditor } from "vue3-ace-editor";
import { Dependencies } from "@/types/notebook_response";
import { DependencyRequest } from "@/types/dependency_request";
import "ace-builds/src-noconflict/mode-text";
import "ace-builds/src-noconflict/snippets/text";
import "ace-builds/src-noconflict/ext-language_tools";
import "ace-builds/src-noconflict/theme-dracula";
import axios from "axios";

export default {
    components: {
        "ace-editor": VAceEditor,   
    },
    data: () => ({
        updatingDependencies: false
    }),
    props: {
        dependencies: {
            type: Object as PropType<Dependencies>,
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
                minlines: 1,
                maxLines: Infinity,
            };
        }
    },
    methods: {
        async updateDependencies() {
            const request: DependencyRequest = {dependencies: this.dependencies.value}
            const response = await axios.post(
                import.meta.env.VITE_BACKEND_URL + "api/dependency_update",
                request
            );
            this.updatingDependencies = false;
        }
    }
}
</script>