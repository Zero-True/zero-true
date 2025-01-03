<template>
  <v-list-item-title 
    @click="handleOpen"
    class="d-flex align-center cursor-pointer hover-bg pa-2 rounded"
  >
    <v-icon size="small" class="mr-2">mdi-pencil</v-icon>
    Edit
  </v-list-item-title>

  <v-dialog
    v-model="dialog"
    max-width="900px"
    persistent
    @click:outside="handleClose"
    transition="dialog-bottom-transition"
  >
    <v-overlay
      v-model="loading"
      class="align-center justify-center"
      contained
    >
      <v-progress-circular
        indeterminate
        color="primary"
      ></v-progress-circular>
    </v-overlay>

    <v-card :theme="isDark ? 'dark' : 'light'" class="editor-dialog">
      <!-- Error State -->
      <template v-if="error">
        <v-card-title class="d-flex justify-space-between align-center pa-4">
          <div class="d-flex align-center">
            <v-icon size="small" class="mr-2" color="error">mdi-alert-circle</v-icon>
            <span class="text-h6 text-error">Error Opening File</span>
          </div>
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="handleClose"
            class="ml-2"
          />
        </v-card-title>
        <v-card-text class="pa-6">
          <v-alert
            type="error"
            variant="tonal"
            class="mb-0"
          >
            {{ errorMessage }}
          </v-alert>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn
            color="grey"
            variant="text"
            @click="handleClose"
            class="ml-2"
          >
            Close
          </v-btn>
        </v-card-actions>
      </template>

      <!-- Editor State -->
      <template v-else>
        <v-card-title class="d-flex justify-space-between align-center pa-4 editor-header">
          <div class="d-flex align-center">
            <v-icon size="small" class="mr-2">mdi-file-document-outline</v-icon>
            <span class="text-h6">{{ fileName }}</span>
          </div>
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="handleClose"
            class="ml-2"
          />
        </v-card-title>
        <v-card-subtitle class="pa-2 d-flex align-center editor-subtitle">
          <v-icon size="small" class="mr-2">mdi-file-document-outline</v-icon>
          <span class="text-caption">{{ getFileExtension }}</span>
          <v-divider vertical class="mx-2" />
          <span class="text-caption">{{ getFileSize }}</span>
        </v-card-subtitle>
        <v-card-text class="pa-0 editor-content">
          <div class="editor-container">
            <codemirror
              v-model="fileContent"
              :style="{ height: '600px' }"
              :autofocus="true"
              :indent-with-tab="true"
              :tab-size="2"
              :extensions="extensions"
              @ready="handleReady"
              :id="'fileEditor'"
              class="rounded-0"
            />
          </div>
        </v-card-text>
        <v-card-actions class="pa-4 editor-actions">
          <v-spacer />
          <v-btn
            color="primary"
            variant="elevated"
            @click="saveChanges"
            :loading="saving"
            :disabled="!hasChanges"
            class="px-6"
          >
            <v-icon left class="mr-2">mdi-content-save</v-icon>
            Save Changes
          </v-btn>
          <v-btn
            variant="text"
            @click="handleClose"
            :disabled="saving"
            class="ml-2"
          >
            Cancel
          </v-btn>
        </v-card-actions>
      </template>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, shallowRef, computed } from 'vue'
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
import { useTheme } from 'vuetify'

const props = defineProps<{
  fileName: string
  filePath: string
}>()

const emit = defineEmits<{
  (e: 'file-saved'): void
}>()

const theme = useTheme()
const isDark = computed(() => theme.global.current.value.dark)

const dialog = ref(false)
const fileContent = ref('')
const originalContent = ref('')
const saving = ref(false)
const loading = ref(false)
const view = shallowRef<EditorView | null>(null)
const error = ref(false)
const errorMessage = ref('')

// Compute if there are unsaved changes
const hasChanges = computed(() => {
  return fileContent.value !== originalContent.value
})

// Get file extension for the status bar
const getFileExtension = computed(() => {
  const ext = props.fileName.split('.').pop()?.toLowerCase() || ''
  return ext ? `.${ext.toUpperCase()}` : 'Plain Text'
})

// Get file size for status bar
const getFileSize = computed(() => {
  const bytes = new Blob([fileContent.value]).size
  return `${(bytes / 1024).toFixed(1)} KB`
})

const getLanguageExtension = (fileName: string) => {
  const ext = fileName.split('.').pop()?.toLowerCase() || ''
  switch (ext) {
    case 'py': return python()
    case 'js':  return javascript()
    case 'md': return markdown()
    case 'sql': return sql()
    case 'html': return html()
    default: return []
  }
}

const extensions = computed(() => [
  getLanguageExtension(props.fileName),
  indentUnit.of("    "),
  isDark.value ? oneDark : [],
  EditorView.theme({
    "&": {
      fontSize: "14px",
      height: "100%",
      backgroundColor: isDark.value ? 'rgb(40, 44, 52)' : 'white',
      color: isDark.value ? 'rgb(171, 178, 191)' : 'rgb(60, 60, 60)'
    }
  })
].filter(Boolean))

const loadFile = async () => {
  loading.value = true
  error.value = false
  try {
    const response = await axios.get(
      `${import.meta.env.VITE_BACKEND_URL}api/read_file`,
      { params: { path: props.filePath } }
    )
    fileContent.value = response.data.content
    originalContent.value = response.data.content
  } catch (err: any) {
    error.value = true
    errorMessage.value = err.response?.data?.detail || 'Failed to open file'
  } finally {
    loading.value = false
  }
}

const handleOpen = async () => {
  dialog.value = true
  await loadFile()
}

const handleClose = () => {
  if (hasChanges.value && !error.value) {
    if (confirm('You have unsaved changes. Are you sure you want to close?')) {
      closeDialog()
    }
  } else {
    closeDialog()
  }
}

const closeDialog = () => {
  dialog.value = false
  fileContent.value = ''
  originalContent.value = ''
  error.value = false
  errorMessage.value = ''
}

const saveChanges = async () => {
  saving.value = true
  const chunkSize = 1024 * 512
  const totalChunks = Math.ceil(fileContent.value.length / chunkSize)
  
  try {
    for (let i = 0; i < totalChunks; i++) {
      const chunk = fileContent.value.slice(i * chunkSize, (i + 1) * chunkSize)
      await axios.post(`${import.meta.env.VITE_BACKEND_URL}api/write_file`, {
        path: props.filePath,
        content: chunk,
        chunk_index: i,
        total_chunks: totalChunks,
      })
    }
    emit('file-saved')
    closeDialog()
  } catch (err: any) {
    error.value = true
    errorMessage.value = err.response?.data?.detail || 'Failed to save file'
  } finally {
    saving.value = false
  }
}

const handleReady = (payload: { view: EditorView }) => {
  view.value = payload.view
}
</script>

<style scoped>
.editor-dialog {
  --surface-dark: rgb(40, 44, 52);
  --surface-light: rgb(255, 255, 255);
  --text-dark: rgb(255, 255, 255);
  --text-light: rgb(60, 60, 60);
  --border-dark: rgba(255, 255, 255, 0.12);
  --border-light: rgba(0, 0, 0, 0.12);
}

.editor-header {
  background-color: v-bind("isDark ? 'var(--surface-dark)' : 'var(--surface-light)'");
  color: v-bind("isDark ? 'var(--text-dark)' : 'var(--text-light)'");
  border-bottom: 1px solid v-bind("isDark ? 'var(--border-dark)' : 'var(--border-light)'");
}

.editor-subtitle {
  background-color: v-bind("isDark ? 'var(--surface-dark)' : 'var(--surface-light)'");
  color: v-bind("isDark ? 'var(--text-dark)' : 'var(--text-light)'");
  border-bottom: 1px solid v-bind("isDark ? 'var(--border-dark)' : 'var(--border-light)'");
}

.editor-content {
  background-color: v-bind("isDark ? 'var(--surface-dark)' : 'var(--surface-light)'");
}

.editor-container {
  background-color: v-bind("isDark ? 'var(--surface-dark)' : 'var(--surface-light)'");
}

.editor-actions {
  background-color: v-bind("isDark ? 'var(--surface-dark)' : 'var(--surface-light)'");
  border-top: 1px solid v-bind("isDark ? 'var(--border-dark)' : 'var(--border-light)'");
}

:deep(.cm-editor) {
  height: 100%;
}

:deep(.cm-scroller) {
  font-family: 'Fira Code', monospace;
}
:deep(.editor-actions .v-btn--variant-text) {
  color: var(--v-theme-on-surface) !important;
}
</style>