<template>
      <v-main>
        <v-container>
          <v-menu v-if="$devMode" transition="scale-transition">
            <template v-slot:activator="{ props }">
              <v-btn v-bind="props" block>
                <v-row>
                  <v-icon color="primary">mdi-plus</v-icon>
                </v-row>
              </v-btn>
            </template>
  
            <v-list>
              <v-list-item v-for="(item, i) in menu_items" :key="i">
                <v-btn block @click="createCodeCell('', item.title)">{{ item.title }}</v-btn>
              </v-list-item>
            </v-list>
          </v-menu>
        </v-container>
        <v-container v-for="codeCell in notebook.cells">
          
          <component v-if="codeCell.cellType==='code'"
            :is="getComponent(codeCell.cellType)"
            :cellData="codeCell"
            :completions="completions[codeCell.id]"
            @runCode="runCode"
            @saveCell="saveCell"
            @componentChange="componentValueChange"
            @deleteCell="deleteCell"
            @createCell="createCodeCell"
          />
          <component v-else
            :is="getComponent(codeCell.cellType)"
            :cellData="codeCell"
            @runCode="runCode"
            @saveCell="saveCell"
            @componentChange="componentValueChange"
            @deleteCell="deleteCell"
            @createCell="createCodeCell"
          />
        </v-container>
      </v-main>
  </template>
  
  <script lang="ts">
  import { Notebook, CodeCell, Layout } from "@/types/notebook";
  import CodeComponent from "@/components/CodeComponent.vue";
  import MarkdownComponent from "@/components/MarkdownComponent.vue";
  import EditorComponent from "@/components/EditorComponent.vue";
  import SQLComponent from "@/components/SQLComponent.vue";
  import PackageComponent from "@/components/PackageComponent.vue";
import { PropType } from "vue";
  
  export default {
    
    props: {
      notebook: {
        type: Object as PropType<Notebook>,
        required: true,
      },
      completions: {
        type: Object as PropType<{ [key: string]: string[] }>,
        required: true,
      },
    },

    components: {
      CodeComponent,
      MarkdownComponent,
      EditorComponent,
      SQLComponent,
      PackageComponent
    },
  
    data() {
      return {
        menu_items: [
            { title: 'Code' },
            { title: 'SQL' },
            { title: 'Markdown' },
            { title: 'Text' },
          ],
        concatenatedCodeCache: {
        lastCellId: '' as string,
        code: '' as string,
        length: 0 as number
      }
      };
    },
  
  
    
    methods: {
      getComponent(cellType: string) {
        switch (cellType) {
          case "code":
            return "CodeComponent";
          case "text":
            return "EditorComponent";
          case "markdown":
            return "MarkdownComponent";
          case "sql":
            return "SQLComponent";
          default:
            throw new Error(`Unknown component type: ${cellType}`);
        }
      },
    
      runCode(cellId: string, componentId: string, code: string) {
        this.$emit("runCode", cellId,componentId);
      },
      deleteCell(cellId: string) {
        this.$emit("deleteCell", cellId);
      },
      saveCell(cellId: string, text: string, line: string, column: string) {
        this.$emit("saveCell", cellId, text, line, column);
      },
      createCodeCell(position_key: string, cellType: string) {
        this.$emit("createCell", position_key, cellType);
      },
      componentValueChange(cell: CodeCell, componentId: string, componentValue: any) {
        this.$emit("componentChange", cell, componentId, componentValue);
      },
    
    }};
  </script>
  
  <style>
  .cm-editor {
    height: auto !important;
  }
  </style>
  