<template>
    <v-list-item-title 
      @click="handleOpen"
      class="d-flex align-center cursor-pointer hover-delete pa-2 rounded"
    >
      <v-icon size="small" class="mr-2">mdi-delete</v-icon>
      Delete
    </v-list-item-title>

    <v-dialog
      v-model="dialog"
      max-width="450px"
      persistent
      @click:outside="handleClose"
      transition="dialog-bottom-transition"
    >
      <v-card class="delete-dialog">
        <!-- Dark themed header -->
        <v-card-title class="d-flex justify-space-between align-center pa-4 bg-dark">
          <div class="d-flex align-center">
            <v-icon size="small" class="mr-2">mdi-alert-circle</v-icon>
            <span class="text-h6">Confirm Deletion</span>
          </div>
        <v-btn
          icon
          @click="handleClose"
          class="close-button"
        >
          <v-icon size="20">mdi-close</v-icon>
        </v-btn>
        </v-card-title>

        <!-- Item details -->
        <v-card-text class="pa-4 pb-0 bg-dark">
          <div class="mb-4 text-grey-lighten-2">
            <div class="d-flex align-center mb-3">
              <v-icon 
                size="large" 
                class="mr-3" 
                :color="isFolder ? 'warning' : 'grey'"
              >mdi-file-document-outline</v-icon>
              <div>
                <div class="text-h6">{{ fileName }}</div>
                <div class="text-caption">{{ getItemType }}</div>
              </div>
            </div>
            
            <div class="text-body-1 mb-4">
              Are you sure you want to delete this {{ isFolder ? 'folder' : 'file' }}? 
              This action cannot be undone.
            </div>

            <!-- Extra warning for folders -->
            <v-alert
              v-if="isFolder"
              type="warning"
              variant="tonal"
              class="mb-4"
              color="warning"
            >
              <template v-slot:prepend>
                <v-icon>mdi-folder-alert</v-icon>
              </template>
              <div>
                <strong>Warning: Folder Will Be Deleted</strong>
                <div class="text-caption">
                  This folder and its contents will be permanently deleted. Please confirm before proceeding.
                </div>
              </div>
            </v-alert>
          </div>
        </v-card-text>

        <!-- Dark themed action buttons -->
        <v-card-actions class="pa-4 bg-dark">
          <v-spacer />
          <v-btn
            color="grey"
            variant="text"
            @click="handleClose"
            :disabled="deleting"
            class="cancel-button"
          >
            Cancel
          </v-btn>
          <v-btn
            variant="elevated"
            @click="deleteItem"
            :loading="deleting"
            class="px-6"
            color="primary"
          >
            <v-icon left class="mr-2">mdi-delete</v-icon>
            Delete {{ isFolder ? 'Folder' : 'File' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Enhanced error snackbar -->
    <v-snackbar
      v-model="showError"
      :color="snackbarColor"
      :timeout="5000"
      location="top"
    >
      <div class="d-flex align-center">
        <v-icon size="small" class="mr-2">mdi-alert-circle</v-icon>
        {{ errorMessage }}
      </div>
      <template v-slot:actions>
        <v-btn
          color="white"
          variant="text"
          @click="showError = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import axios from 'axios'

export default defineComponent({
  name: 'DeleteDialog',
  props: {
    fileName: {
      type: String,
      required: true
    },
    filePath: {
      type: String,
      required: true
    },
    isProtectedFile: {
      type: Function,
      required: true
    }
  },
  emits: ['item-deleted'],

  setup(props, { emit }) {
    const dialog = ref(false)
    const deleting = ref(false)
    const errorMessage = ref('')
    const showError = ref(false)
    const snackbarColor = ref('error')

    const isFolder = computed(() => !props.fileName.includes('.'))
    
    const getItemType = computed(() => isFolder.value ? 'Folder' : 'File')

    const displayError = (message: string, isWarning = false) => {
      errorMessage.value = message
      snackbarColor.value = isWarning ? 'warning' : 'error'
      showError.value = true
    }

    const handleOpen = () => {
      if (!props.isProtectedFile(props.fileName)) {
        dialog.value = true
        // Reset previous state
        deleting.value = false
        errorMessage.value = ''
        showError.value = false
      }
    }

    const handleClose = () => {
      dialog.value = false
    }

    const deleteItem = async () => {
      deleting.value = true
      try {
        const response = await axios.post(`${import.meta.env.VITE_BACKEND_URL}api/delete_item`, {
          path: props.filePath,
        })
        if (response.data.success) {
          emit('item-deleted')
          handleClose()
        } else {
          displayError(response.data.message || 'Failed to delete item')
        }
      } catch (error: any) {
        const status = error.response?.status
        const errorMsg = error.response?.data?.detail || 'Error connecting to the server'
        console.error('Error deleting item:', error)

        switch (status) {
          case 400:
            displayError(errorMsg, true)
            break
          case 403:
            displayError('Permission denied. Unable to delete the item.')
            break
          case 404:
            displayError('Item not found. It may have been already deleted.')
            break
          case 500:
            displayError(`Server error: ${errorMsg}`)
            break
          default:
            displayError(errorMsg)
        }
      } finally {
        deleting.value = false
      }
    }

    return {
      dialog,
      deleting,
      errorMessage,
      showError,
      snackbarColor,
      isFolder,
      getItemType,
      handleOpen,
      handleClose,
      deleteItem
    }
  }
})
</script>


<style scoped>

.close-button {
  position: absolute;
  top: 8px;
  right: 8px;
  color: var(--v-theme-on-surface) !important;
}

.cancel-btn {
  /* Forces button text to use the current theme’s on-surface color */
  color: var(--v-theme-on-surface) !important;
}


.cursor-pointer {
  cursor: pointer;
}
:deep(.v-alert) {
  background-color: rgba(255, 171, 0, 0.1) !important;
}
</style>