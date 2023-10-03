<template>
    <v-card flat color="bluegrey">
        <tiny-editor v-if="$devMode" v-model="cellData.code" :init="init"/>
        <tiny-editor v-else v-model="cellData.code" :init="init" :disabled="true"/>
        <v-toolbar v-if="$devMode" color="bluegrey">
            <v-spacer/>
            <v-btn variant="flat" color="error" @click="deleteCell">Delete Cell</v-btn>
        </v-toolbar>
    </v-card>
</template>

<script lang="ts">
import type { PropType } from 'vue'
import "tinymce/tinymce";
import 'tinymce/models/dom';
import "tinymce/themes/silver";
import "tinymce/icons/default";
import "tinymce/skins/ui/tinymce-5-dark/skin.css";
import "tinymce/plugins/autoresize";
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
        if (this.$devMode){
            return {
                init: {
                    plugins: 'autoresize',
                    toolbar:
                    'undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist | forecolor backcolor removeformat | pagebreak | charmap emoticons | fullscreen  preview save print | insertfile image media template link anchor codesample | ltr rtl',
                    branding: false,
                    menubar: false,
                    statusbar: false,
                    skin: false,
                    content_css: false,
                    content_style: "body { background-color: #1B2F3C; color: #FFFFFF; } main { border-radius: 0; }",
                    autoresize_bottom_margin: 10,
                    min_height: 300,
                }
            };
        }
        else{
            return {
                init: {
                    plugins: 'autoresize',
                    toolbar: false,
                    branding: false,
                    menubar: false,
                    statusbar: false,
                    skin: false,
                    content_css: false,
                    content_style: "body { background-color: #1B2F3C; color: #FFFFFF; } main { border-radius: 0; }"
                }
            };
        }
        
    },
    methods: {
        deleteCell(){
            this.$emit('deleteCell', this.cellData.id);
        }
    },
}
</script>
<style>
.tox .tox-toolbar, .tox .tox-toolbar__primary, .tox .tox-toolbar__overflow {
    background-color: #0E1B23 !important;
}
</style>