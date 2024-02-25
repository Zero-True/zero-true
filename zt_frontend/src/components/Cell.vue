<template>
  <v-card v-if="isDevMode || (!isDevMode && !hideCellValue)" :id="'codeCard' + cellId" :class="['cell', {'cell--dev': isDevMode }]" color="bluegrey-darken-4">
    <v-divider class="indicator" vertical :color="dividerColor" :thickness="4"></v-divider>
    <div class="content">
      <header class="header" v-if="isDevMode">
        <div class="click-edit">
          <div class="click-edit__show-text" v-if="!editingCellName">
            <h4 class="text-bluegrey-darken-1 text-ellipsis click-edit__name" @click="toggleCellName">{{ cellNameValue }} </h4>
            <!-- <v-btn
              v-if="isDevMode"
              color="bluegrey-darken-4"
              :icon="`ztIcon:${ztAliases.edit}`"
              size="x-small"
              class="text-bluegrey-darken-1"
              @click="toggleCellName"
            /> -->
          </div> 
          
          <div class="click-edit__edit-field-wrapper" v-if="editingCellName">
            <v-text-field 
              v-model="cellNameEditValue"   
              :placeholder=cellType
              density="compact" 
              variant="plain"
              hide-details
              ref="cellNameField" 
              class="click-edit__edit-field" 
              @keydown.enter="saveCellName"
              @update:focused="focused => { if(!focused) saveCellName() }"
            />
            <!-- <v-btn
              color="bluegrey-darken-4"
              :icon="`ztIcon:${ztAliases.save}`"
              size="x-small"
              @click="saveCellName"
            /> -->
            <!-- <v-btn
              color="bluegrey-darken-4"
              icon="$close"
              size="x-small"
              @click="toggleCellName"
            /> -->
          </div> 
        </div>
        <v-defaults-provider :defaults="{
          'VIcon': {
            'color': 'bluegrey',
          },
          'VBtn': {
            variant: 'text',
            size: 'small'
          }
        }">
          <div class="actions">
            <!-- <v-btn icon="$message"></v-btn> -->
            <v-btn v-if="showSaveBtn" :icon="`ztIcon:${ztAliases.save}`" @click="$emit('save')"></v-btn>

            <v-btn v-if="showPlayBtn" :id="'runCode' + cellId" :icon="`ztIcon:${ztAliases.play}`"
              @click="$emit('play')"></v-btn>
            <v-menu :close-on-content-click="false">
              <template v-slot:activator="{ props }">
                <v-btn :icon="`ztIcon:${ztAliases.settings}`" v-bind="props"></v-btn>
              </template>

              <v-list>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-switch v-model="hideCellValue" @update:modelValue="updateHideCell"></v-switch>
                  </template>
                  <v-list-item-title>Hide Cell</v-list-item-title>
                </v-list-item>
                <v-list-item v-if="keepCodeInAppModel">
                  <template v-slot:prepend>
                    <v-switch v-model="hideCodeValue" @update:modelValue="updateHideCode"></v-switch>
                  </template>
                  <v-list-item-title>Hide Code</v-list-item-title>
                </v-list-item>
                <v-list-item v-if="keepCodeInAppModel">
                  <template v-slot:prepend>
                    <v-switch v-model="expandCodeValue" @update:modelValue="updateExpandCode"></v-switch>
                  </template>
                  <v-list-item-title>Expand Code</v-list-item-title>
                </v-list-item>
                <v-list-item v-if="keepCodeInAppModel">
                  <template v-slot:prepend>
                    <v-switch v-model="nonReactiveValue" @update:modelValue="updateReactivity"></v-switch>
                  </template>
                  <v-list-item-title>Non-Reactive</v-list-item-title>
                </v-list-item>
              </v-list>

            </v-menu>
            <v-menu>
              <template v-slot:activator="{ props }">
                <v-btn :icon="`ztIcon:${ztAliases.more}`" :id="'cellToolbar' + cellId" v-bind="props"></v-btn>
              </template>
              <v-list>
                <!-- <v-list-item>
                  <template v-slot:prepend>
                    <v-icon icon="$collapse"></v-icon>
                  </template>
                  <v-list-item-title>Move Up</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon icon="$expand"></v-icon>
                  </template>
                  <v-list-item-title>Move Down</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon :icon="`ztIcon:${ztAliases.duplicate}`"></v-icon>
                  </template>
                  <v-list-item-title>Duplicate</v-list-item-title>
                </v-list-item> -->
                <v-list-item base-color="error" :id="'deleteCell' + cellId" @click="$emit('delete')">
                  <template v-slot:prepend>
                    <v-icon :icon="`ztIcon:${ztAliases.delete}`"></v-icon>
                  </template>
                  <v-list-item-title>Delete Cell</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </v-defaults-provider>
      </header>
      <div 
        :class="[
          'code',
          {'code--dev': isDevMode}
        ]"
        v-if="isDevMode || (!isDevMode && keepCodeInAppModel && !hideCodeValue)"
      >
        <slot name="code"></slot>
      </div>
      <div 
        :class="[
          'outcome',
          {'outcome--dev': isDevMode}
        ]"
        v-if="!(isDevMode && !isAppRoute && cellType==='text')" 
      >
        <slot name="outcome"></slot>
      </div>
    </div>
    <v-tooltip v-if="nonReactiveValue" text="Cell is Stale">
      <template v-slot:activator="{ props }">
        <v-divider v-bind="props" class="indicator" vertical color="warning" :thickness="8"/>
      </template>
    </v-tooltip>
  </v-card>
  <add-cell v-if="isDevMode" :cell-id="cellId" @createCodeCell="e => $emit('addCell', e)" />
</template>
<script setup lang="ts">
import axios from 'axios'
import { computed, PropType, nextTick, ref } from 'vue'
import type { Celltype } from '@/types/create_request'
import { ztAliases } from '@/iconsets/ztIcon'
import { useRoute } from 'vue-router'
import type { VTextField } from "vuetify/lib/components/index.mjs";
import AddCell from '@/components/AddCell.vue'
import { HideCellRequest } from '@/types/hide_cell_request'
import { HideCodeRequest } from '@/types/hide_code_request'
import { ExpandCodeRequest } from '@/types/expand_code_request'
import { CellReactivityRequest } from '@/types/cell_reactivity_request'
import { NameCellRequest } from '@/types/name_cell_request'

const props = defineProps({
  isDevMode: Boolean,
  cellType: String as PropType<Celltype>,
  cellId: String,
  error: Boolean,
  hideCell: {
    type: Boolean,
    default: false
  },
  hideCode: {
    type: Boolean,
    default: false
  },
  expandCode: {
    type: Boolean,
    default: false
  },
  nonReactive: {
    type: Boolean,
    default: false
  },
  cellName: {
    type: String,
    default: null
  }
})
const emits = defineEmits<{
  (e: 'delete'): void
  (e: 'play'): void
  (e: 'save'): void
  (e: 'expandCodeUpdate', expand: Boolean): void
  (e: 'updateReactivity', expand: Boolean): void
  (e: 'addCell', cellType: Celltype): void
}>()

const dividerColor = computed(() => {
  if (props.error) return 'error' 
  switch (props.cellType) {
    case 'markdown':
      return '#4CBCFC';
    case 'code':
      return '#AE9FE8'
    case 'sql':
      return '#FFDCA7';
    case 'text':
      return '#16B48E';
  }
})

const hideCellValue = ref(props.hideCell || false);
const hideCodeValue = ref(props.hideCode || false);
const expandCodeValue = ref(props.expandCode || false);
const nonReactiveValue = ref(props.nonReactive || false);
const cellNameValue = ref(props.cellName || props.cellType);
const cellNameEditValue = ref('');
const cellNameField = ref(null);
const editingCellName = ref(false);
const showPlayBtn = computed(() => props.cellType === 'code' || props.cellType === 'sql')
const showSaveBtn = computed(() => props.cellType === 'markdown' || props.cellType === 'text') 
const keepCodeInAppModel = computed(() => props.cellType === 'code' || props.cellType === 'sql') 
const isAppRoute = computed(() => useRoute().name === '/app')

const updateHideCell = async (value: unknown) => {
  const hideCodeRequest: HideCellRequest = {
    cellId: props.cellId as string,
    hideCell: value as boolean
  }
  await axios.post(import.meta.env.VITE_BACKEND_URL + "api/hide_cell", hideCodeRequest);
};
const updateHideCode = async (value: unknown) => {
  const hideCodeRequest: HideCodeRequest = {
    cellId: props.cellId as string,
    hideCode: value as boolean
  }
  await axios.post(import.meta.env.VITE_BACKEND_URL + "api/hide_code", hideCodeRequest);
};
const updateExpandCode = async (value: unknown) => {
  const expandCodeRequest: ExpandCodeRequest = {
    cellId: props.cellId as string,
    expandCode: value as boolean
  }
  await axios.post(import.meta.env.VITE_BACKEND_URL + "api/expand_code", expandCodeRequest);
  emits('expandCodeUpdate', value as boolean)
};
const updateReactivity = async (value: unknown) => {
  const cellReactivityRequest: CellReactivityRequest = {
    cellId: props.cellId as string,
    nonReactive: value as boolean
  }
  await axios.post(import.meta.env.VITE_BACKEND_URL + "api/cell_reactivity", cellReactivityRequest);
  emits('updateReactivity', value as boolean)
};

const toggleCellName = () => {
  editingCellName.value = !editingCellName.value
  if (editingCellName.value) {
    cellNameEditValue.value = cellNameValue.value as string
    nextTick(() => {
      if (cellNameField.value){
        (cellNameField.value as VTextField).focus();
      }
    }) 
  }
}

const saveCellName = async () => {
  const nameCellRequest: NameCellRequest = {
    cellId: props.cellId as string,
    cellName: cellNameEditValue.value as string
  }
  await axios.post(import.meta.env.VITE_BACKEND_URL + "api/rename_cell", nameCellRequest);
  cellNameValue.value = cellNameEditValue.value
  editingCellName.value = false
}
</script>

<style lang="scss" scoped>
.cell {
  padding: 24px;
  display: flex;
  margin-bottom: 2px;
  &--dev {
    margin-bottom: 16px;
  }
}

.content {
  flex: 1;
  margin-left: 16px;
  margin-right: 0px;
  width: calc(100% - 36px);
}

.indicator {
  border-radius: 4px;
}

.header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.code,
.outcome {
  padding: 0px;
  &--dev {
    border: 1px solid rgba(var(--v-theme-bluegrey));
    border-radius: 4px;
    padding: 12px;
  }
}

.code {
  margin-bottom: 16px;
}

.click-edit {
  max-width: 250px;
  width: 100%;
  &__name {
    cursor: pointer; 
    font-weight: normal;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  &__show-text,
  &__edit-field-wrapper {
    height: 100%;
    display: flex;
    align-items: center;
  }

  &__edit-field {
    margin-top: -11px; 
    & :deep(.v-field__input) {
      font-size: 1rem;
      letter-spacing: normal;
    }
  }
}
</style>
