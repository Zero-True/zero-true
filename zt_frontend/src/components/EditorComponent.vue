<template>
    <v-card flat>
        <quill-editor toolbar="essential" :options="options"/>
        <v-toolbar>
            <v-spacer/>
            <v-btn small color="primary" @click="deleteCell">Delete Cell</v-btn>
        </v-toolbar>
    </v-card>
</template>

<script lang="ts">
import type { PropType } from 'vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css';
import { CodeCell } from '@/types/notebook';

export default {
    components: {
        'quill-editor': QuillEditor
    },
    props: {
        cellData: {
            type: Object as PropType<CodeCell>,
            required: true,
        },
    },
    data() {
        return {
            options: {
                placeholder: this.cellData.code,
                theme: 'snow'
            }
        }
    },
    methods: {
        deleteCell(){
            this.$emit('deleteCell', this.cellData.id);
        }
    },
}
</script>

<style scoped>
.ql-container.ql-snow{ border: none !important;}
</style>