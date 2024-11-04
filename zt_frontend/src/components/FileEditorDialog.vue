<template>
    <v-dialog v-model="dialog" max-width="800px">
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center pa-4">
          <span>Edit File: {{ fileName }}</span>
          <v-btn icon="mdi-close" variant="text" @click="closeDialog" />
        </v-card-title>
        <v-card-text>
          <codemirror
            v-model="fileContent"
            :style="{ height: '500px' }"
            :autofocus="true"
            :indent-with-tab="true"
            :tab-size="2"
            :extensions="extensions"
            @ready="handleReady"
            :id="'fileEditor'"
          />
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn
            color="primary"
            variant="text"
            @click="saveChanges"
            :loading="saving"
          >
            Save
          </v-btn>
          <v-btn
            color="grey-darken-1"
            variant="text"
            @click="closeDialog"
          >
            Cancel
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, shallowRef } from 'vue'
  import { Codemirror } from 'vue-codemirror'
  import { python } from '@codemirror/lang-python'
  import { javascript } from '@codemirror/lang-javascript'
  import { markdown } from '@codemirror/lang-markdown'
  import { sql } from '@codemirror/lang-sql'
  import { html } from '@codemirror/lang-html'
  import { indentUnit } from '@codemirror/language'
  import { oneDark } from '@codemirror/theme-one-dark'
  import { EditorView } from '@codemirror/view'
  import axios from 'axios'
  
  export default defineComponent({
    name: 'FileEditorDialog',
    components: {
      Codemirror
    },
  
    setup() {
      const dialog = ref(false)
      const fileContent = ref('')
      const fileName = ref('')
      const filePath = ref('')
      const saving = ref(false)
      const view = shallowRef<EditorView | null>(null)
  
      const getLanguageExtension = (fileName: string) => {
        const ext = fileName.split('.').pop()?.toLowerCase() || ''
        switch (ext) {
          case 'py':
            return python()
          case 'js':
          case 'json':
            return javascript()
          case 'md':
            return markdown()
          case 'sql':
            return sql()
          case 'html':
            return html()
          case 'txt':
          case 'log':
          case 'csv':
          case 'text':
            return []
          default:
            return []
          
          }
      }
  
      const openDialog = async (item: { id: string, title: string }) => {
        try {
          fileName.value = item.title
          filePath.value = item.id
          const response = await axios.get(
            `${import.meta.env.VITE_BACKEND_URL}api/read_file`,
            { params: { path: item.id } }
          )
          fileContent.value = response.data.content
          dialog.value = true
        } catch (error) {
          console.error('Error reading file:', error)
        }
      }
  
      const closeDialog = () => {
        dialog.value = false
        fileContent.value = ''
        fileName.value = ''
        filePath.value = ''
      }
  
      const saveChanges = async () => {
        saving.value = true
        try {
          await axios.post(`${import.meta.env.VITE_BACKEND_URL}api/write_file`, {
            path: filePath.value,
            content: fileContent.value
          })
          closeDialog()
        } catch (error) {
          console.error('Error saving file:', error)
        } finally {
          saving.value = false
        }
      }
  
      const handleReady = (payload: { view: EditorView }) => {
        view.value = payload.view
      }
  
      const extensions = computed(() => [
        getLanguageExtension(fileName.value),
        indentUnit.of("    "),
        oneDark
      ])
  
      return {
        dialog,
        fileContent,
        fileName,
        saving,
        extensions,
        handleReady,
        closeDialog,
        saveChanges,
        openDialog
      }
    }
  })
  </script>