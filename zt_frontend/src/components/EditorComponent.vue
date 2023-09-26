<template>
    <v-card flat>
        <tiny-editor v-model="cellData.code" :init="init"/>
        <v-toolbar>
            <v-spacer/>
            <v-btn small color="primary" @click="deleteCell">Delete Cell</v-btn>
        </v-toolbar>
    </v-card>
</template>

<script lang="ts">
import type { PropType } from 'vue'
import "tinymce/tinymce";
import 'tinymce/models/dom';
import "tinymce/themes/silver";
import "tinymce/icons/default";
import "tinymce/skins/ui/oxide-dark/skin.css";
import Editor from "@tinymce/tinymce-vue";
import { CodeCell } from '@/types/notebook';

export default {
    components: {
        'tiny-editor': Editor
    },
    props: {
        cellData: {
            type: Object as PropType<CodeCell>,
            required: true,
        },
    },
    data() {
        return {
            init: {
                height: 500,
                toolbar:
                'undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist | forecolor backcolor removeformat | pagebreak | charmap emoticons | fullscreen  preview save print | insertfile image media template link anchor codesample | ltr rtl',
                branding: false,
                menubar: false,
                skin: false,
                content_css: false,
            }
        };
    },
    methods: {
        deleteCell(){
            this.$emit('deleteCell', this.cellData.id);
        }
    },
}
</script>