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

    <v-card class="editor-dialog">
    <!-- Error State -->
    <template v-if="error">
      <v-card-title class="d-flex justify-space-between align-center pa-4 bg-dark">
        <div class="d-flex align-center">
          <v-icon size="small" class="mr-2" color="error">mdi-alert-circle</v-icon>
          <span class="text-h6 text-error">Error Opening File</span>
        </div>
        <v-btn
          icon="mdi-close"
          variant="text"
          @click="handleClose"
          class="ml-2"
          color="grey-lighten-2"
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
      <v-card-title class="d-flex justify-space-between align-center pa-4 bg-dark">
        <div class="d-flex align-center">
          <v-icon size="small" class="mr-2" color="grey-lighten-2">mdi-file-document-outline</v-icon>
          <span class="text-h6 text-grey-lighten-2">{{ fileName }}</span>
        </div>
        <v-btn
          icon="mdi-close"
          variant="text"
          @click="handleClose"
          class="ml-2"
          color="grey-lighten-2"
        />
      </v-card-title>
      <v-card-subtitle class="pa-2 d-flex align-center bg-dark border-subtle">
        <v-icon size="small" class="mr-2" color="grey-lighten-2">mdi-file-document-outline</v-icon>
        <span class="text-caption text-grey-lighten-2">{{ getFileExtension }}</span>
        <v-divider vertical class="mx-2" color="grey-darken-3" />
        <span class="text-caption text-grey-lighten-2">{{ getFileSize }}</span>
      </v-card-subtitle>
      <v-card-text class="pa-0 bg-dark" style="overflow-y: auto;">
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
      <v-card-actions class="pa-4 bg-dark">
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
          color="grey"
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

<script lang="ts">
import { defineComponent, ref, shallowRef, computed } from 'vue'
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
props: {
  fileName: {
    type: String,
    required: true
  },
  filePath: {
    type: String,
    required: true
  }
},
emits: ['file-saved'],

setup(props, { emit }) {
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



  // Simulate file size for status bar
  const getFileSize = computed(() => {
    const bytes = new Blob([fileContent.value]).size
    return `${(bytes / 1024).toFixed(1)} KB`
  })

  const getLanguageExtension = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase() || ''
    switch (ext) {
      case 'py': return python()
      case 'js':
      case 'json': return javascript()
      case 'md': return markdown()
      case 'sql': return sql()
      case 'html': return html()
      default: return []
    }
  }

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
    loading.value = true
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
    const chunkSize = 1024 * 512;
    const totalChunks = Math.ceil(fileContent.value.length / chunkSize);
    try {
      for (let i = 0; i < totalChunks; i++) {
        const chunk = fileContent.value.slice(i * chunkSize, (i + 1) * chunkSize);

        await axios.post(`${import.meta.env.VITE_BACKEND_URL}api/write_file`, {
          path: props.filePath,
          content: chunk,
          chunk_index: i,
          total_chunks: totalChunks,
        });
      }
      emit('file-saved')
      closeDialog()
    }catch (err: any) {
      error.value = true
      errorMessage.value = err.response?.data?.detail || 'Failed to save file'
    }  finally {
      saving.value = false
    }
  }

  const handleReady = (payload: { view: EditorView }) => {
    view.value = payload.view
  }

  const extensions = computed(() => [
    getLanguageExtension(props.fileName),
    indentUnit.of("    "),
    oneDark,
    EditorView.theme({
      "&": {
        fontSize: "14px",
        height: "100%"
      }
    })
  ])

  return {
    dialog,
    fileContent,
    saving,
    loading,
    extensions,
    hasChanges,
    getFileExtension,
    getFileSize,
    handleReady,
    handleClose,
    handleOpen,
    saveChanges,
    error,
    errorMessage,
  }
}
})
</script>

<style scoped>
.hover-bg:hover {
background-color: rgba(var(--v-theme-primary), 0.1);
}

.cursor-pointer {
cursor: pointer;
}

.editor-dialog {
background-color: #282c34 !important;
border: 1px solid rgba(255, 255, 255, 0.1);
}

.editor-container {
border: 1px solid rgba(255, 255, 255, 0.1);
}

.bg-dark {
background-color: #282c34 !important;
}

.border-subtle {
border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.cm-editor) {
height: 100%;
}

:deep(.cm-scroller) {
font-family: 'Fira Code', monospace;
overflow: auto;
}

/* Dark theme overrides */
:deep(.v-card) {
background-color: #282c34;
color: #abb2bf;
}

:deep(.v-overlay__content) {
background-color: #282c34;
}

:deep(.v-alert) {
background-color: rgba(var(--v-theme-error), 0.1) !important;
}
</style>