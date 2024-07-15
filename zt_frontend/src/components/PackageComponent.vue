<template>
<v-dialog v-model="updatingDependencies" persistent width="1024">
    <template v-slot:activator="{ props }">
        <v-btn v-bind="props" :icon="`ztIcon:${ztAliases.settings}`"></v-btn>
    </template>
    <v-card>
        <v-card-title>
        <span class="text-h5">Add Dependencies</span>
        </v-card-title>
        <codemirror
            v-if="$devMode"
            v-model="dependencies.value"
            :style="{ height: '400px' }"
            :autofocus="true"
            :indent-with-tab="true"
            :tab-size="2"
            :viewportMargin="Infinity"
            :extensions="extensions"
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
</template>

<script lang="ts">
import type { PropType } from "vue";
import { Codemirror } from 'vue-codemirror'
import { markdown } from '@codemirror/lang-markdown'
import { oneDark } from '@codemirror/theme-one-dark'
import { EditorView } from '@codemirror/view'
import { autocompletion, CompletionResult, CompletionContext } from '@codemirror/autocomplete'
import { Dependencies } from "@/types/notebook_response";
import { DependencyRequest } from "@/types/dependency_request";
import axios from "axios";
import { ztAliases } from '@/iconsets/ztIcon'

export default {
    components: {
        "codemirror": Codemirror,  
    },
    data: () => ({
        updatingDependencies: false,
      	ztAliases
    }),
    props: {
        dependencies: {
            type: Object as PropType<Dependencies>,
            required: true,
        },
    },
    computed: {
        extensions() {return [markdown(), oneDark, autocompletion({ override: [] })]},
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