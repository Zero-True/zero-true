<template>
    <v-list-item-title 
      @click="handleOpen"
      class="d-flex align-center cursor-pointer hover-bg pa-2 rounded"
    >
      <v-icon size="small" class="mr-2">mdi-pencil-box</v-icon>
      Rename
    </v-list-item-title>

    <v-dialog
      v-model="dialog"
      max-width="450px"
      persistent
      @click:outside="handleClose"
      transition="dialog-bottom-transition"
    >
      <v-card class="rename-dialog">
        <!-- Dark themed header -->
        <v-card-title class="d-flex justify-space-between align-center pa-4 bg-dark">
          <div class="d-flex align-center">
            <v-icon size="small" class="mr-2" color="grey-lighten-2">mdi-file-document-outline</v-icon>
            <span class="text-h6 text-grey-lighten-2">Rename Item</span>
          </div>
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="handleClose"
            class="ml-2"
            color="grey-lighten-2"
          />
        </v-card-title>

        <!-- Current filename display -->
        <v-card-subtitle class="pa-3 bg-dark border-subtle">
          <div class="text-grey-lighten-2">
            <span class="text-caption">Current name:</span>
            <span class="text-body-2 ml-2">{{ fileName }}</span>
          </div>
        </v-card-subtitle>

        <!-- Rename input -->
        <v-card-text class="pa-4 bg-dark">
          <v-text-field
            v-model="newName"
            label="New Name"
            :rules="nameRules"
            required
            @keyup.enter="saveChanges"
            autofocus
            variant="outlined"
            color="primary"
            bg-color="grey-darken-4"
            class="rename-input"
            persistent-placeholder
            :error-messages="errorMessage"
            theme="dark"
          >
            <template v-slot:prepend-inner>
              <v-icon size="small" color="grey-lighten-2">mdi-form-textbox</v-icon>
            </template>
          </v-text-field>

          <!-- Extension warning if changed -->
          <div v-if="hasExtensionChanged" class="mt-2 text-warning text-caption d-flex align-center">
            <v-icon size="small" color="warning" class="mr-1">mdi-alert-circle</v-icon>
            Warning: Changing the file extension may affect file functionality
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
            :disabled="!isValid"
            class="px-6"
          >
            <v-icon left class="mr-2">mdi-check</v-icon>
            Rename
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

    <!-- Enhanced error snackbar -->
    <v-snackbar
      v-model="showError"
      color="error"
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
  name: 'RenameDialog',
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
  emits: ['item-renamed'],

  setup(props, { emit }) {
    const dialog = ref(false)
    const newName = ref('')
    const saving = ref(false)
    const errorMessage = ref('')
    const showError = ref(false)

    const nameRules = [
      (v: string) => !!v || 'Name is required',
      (v: string) => v.trim().length > 0 || 'Name cannot be empty',
      (v: string) => !v.includes('/') || 'Name cannot contain "/"',
      (v: string) => !v.includes('\\') || 'Name cannot contain "\\"'
    ]

    const isValid = computed(() => {
      return newName.value.trim() && nameRules.every(rule => rule(newName.value) === true)
    })

    const hasExtensionChanged = computed(() => {
      const oldExt = props.fileName.split('.').pop()
      const newExt = newName.value.split('.').pop()
      return oldExt !== newExt && oldExt && newExt
    })

    const displayError = (message: string) => {
      errorMessage.value = message
      showError.value = true
    }

    const handleOpen = () => {
      if (!props.isProtectedFile(props.fileName)) {
        newName.value = props.fileName
        dialog.value = true
      }
    }

    const handleClose = () => {
      dialog.value = false
      newName.value = ''
      errorMessage.value = ''
      showError.value = false
    }

    const saveChanges = async () => {
      if (!isValid.value) {
        return
      }

      saving.value = true
      try {
        console.log("Renaming file with values:", {
            path: props.filePath,
            oldName: props.fileName,
            newName: newName.value.trim()
          });
        const response = await axios.post(
          `${import.meta.env.VITE_BACKEND_URL}api/rename_item`,
          {
            path: props.filePath,
            oldName: props.fileName,
            newName: newName.value.trim()
          }
        )
        
        if (response.data.success) {
          emit('item-renamed')
          handleClose()
        } else {
          displayError(response.data.message || 'Failed to rename item')
        }
      } catch (error: any) {
        console.error('Error renaming item:', error)
        displayError(error.response?.data?.message || 'Error connecting to the server')
      } finally {
        saving.value = false
      }
    }

    return {
      dialog,
      newName,
      saving,
      errorMessage,
      showError,
      nameRules,
      isValid,
      hasExtensionChanged,
      handleOpen,
      handleClose,
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

.rename-dialog {
  background-color: #282c34 !important;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.bg-dark {
  background-color: #282c34 !important;
}

.border-subtle {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* Dark theme overrides */
:deep(.v-card) {
  background-color: #282c34;
  color: #abb2bf;
}

:deep(.rename-input .v-field__input) {
  color: #fff !important;
}

:deep(.v-text-field .v-field--variant-outlined) {
  border-color: rgba(255, 255, 255, 0.1);
}

:deep(.v-text-field .v-label) {
  color: rgba(255, 255, 255, 0.7);
}
</style>