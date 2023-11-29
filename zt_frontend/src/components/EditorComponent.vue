<template>
  <v-card flat color="bluegrey">
    <v-row v-if="$devMode" no-gutters class="py-1 toolbar-bg">
      <v-col :cols="11">
        <span class="py-0 px-2">.doc</span>
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
    <tiny-editor v-if="$devMode" v-model="cellData.code" :init="init" />
    <tiny-editor v-else v-model="cellData.code" :init="init" :disabled="true" />
  </v-card>
  <v-menu transition="scale-transition">
    <template v-slot:activator="{ props }">
      <v-btn v-bind="props" block>
        <v-row>
          <v-icon color="primary">mdi-plus</v-icon>
        </v-row>
      </v-btn>
    </template>

    <v-list>
      <v-list-item v-for="(item, i) in items" :key="i">
        <v-btn block @click="createCell(item.title)">{{ item.title }}</v-btn>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script lang="ts">
import type { PropType } from "vue";
import "tinymce/tinymce";
import "tinymce/models/dom";
import "tinymce/themes/silver";
import "tinymce/icons/default";
import "tinymce/skins/ui/tinymce-5-dark/skin.css";
import "tinymce/plugins/autoresize";
import Editor from "@tinymce/tinymce-vue";
import { CodeCell } from "@/types/notebook";

export default {
  components: {
    "tiny-editor": Editor,
  },
  props: {
    cellData: {
      type: Object as PropType<CodeCell>,
      required: true,
    },
  },
  data() {
    if (this.$devMode) {
      return {
        init: {
          plugins: "autoresize",
          toolbar:
            "undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist | forecolor backcolor removeformat | pagebreak | charmap emoticons | fullscreen  preview save print | insertfile image media template link anchor codesample | ltr rtl",
          branding: false,
          menubar: false,
          statusbar: false,
          skin: false,
          content_css: false,
          content_style:
            "body { background-color: #1B2F3C; color: #FFFFFF; } main { border-radius: 0; }",
          autoresize_bottom_margin: 10,
          min_height: 100,
        },
        items: [
          { title: 'Code' },
          { title: 'SQL' },
          { title: 'Markdown' },
          { title: 'Text' },
        ],
      };
    } else {
      return {
        init: {
          plugins: "autoresize",
          toolbar: false,
          branding: false,
          menubar: false,
          statusbar: false,
          skin: false,
          content_css: false,
          content_style:
            "body { background-color: #1B2F3C; color: #FFFFFF; } main { border-radius: 0; }",
        },
        items: [
          { title: 'Code' },
          { title: 'SQL' },
          { title: 'Markdown' },
          { title: 'Text' },
        ],
      };
    }
  },
  methods: {
    saveCell() {
      this.$emit("saveCell", this.cellData.id);
    },
    deleteCell() {
      this.$emit("deleteCell", this.cellData.id);
    },
    createCell(cellType: string){
      this.$emit("createCell", this.cellData.id, cellType);
    }
  },
};
</script>
<style>
.tox .tox-toolbar,
.tox .tox-toolbar__primary,
.tox .tox-toolbar__overflow {
  background-color: #0e1b23 !important;
}
</style>
