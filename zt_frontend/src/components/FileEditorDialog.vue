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
        <!-- Dark themed header -->
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

        <!-- Dark themed status bar -->
        <v-card-subtitle class="pa-2 d-flex align-center bg-dark border-subtle">
          <v-icon size="small" class="mr-2" color="grey-lighten-2">mdi-file-document-outline</v-icon>
          <span class="text-caption text-grey-lighten-2">{{ getFileExtension }}</span>
          <v-divider vertical class="mx-2" color="grey-darken-3" />
          <span class="text-caption text-grey-lighten-2">{{ getFileSize }}</span>
        </v-card-subtitle>

        <!-- Editor container with dark theme -->
        <v-card-text class="pa-0 bg-dark">
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

        <!-- Dark themed action buttons -->
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

    const handleOpen = async () => {
      dialog.value = true
      loading.value = true
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_BACKEND_URL}api/read_file`,
          { params: { path: props.filePath } }
        )
        fileContent.value = response.data.content
        originalContent.value = response.data.content
      } catch (error) {
        console.error('Error reading file:', error)
      } finally {
        loading.value = false
      }
    }

    const handleClose = () => {
      if (hasChanges.value) {
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
    }

    const saveChanges = async () => {
      saving.value = true
      try {
        await axios.post(`${import.meta.env.VITE_BACKEND_URL}api/write_file`, {
          path: props.filePath,
          content: fileContent.value
        })
        emit('file-saved')
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
      saveChanges
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
}

/* Dark theme overrides */
:deep(.v-card) {
  background-color: #282c34;
  color: #abb2bf;
}

:deep(.v-overlay__content) {
  background-color: #282c34;
}
</style>