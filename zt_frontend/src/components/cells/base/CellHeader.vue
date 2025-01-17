<template>
  <header v-if="isFocused || isMenuOpen || showHeader" class="header">
    <CellNameEditor
      v-model="cellNameValue"
      :is-dev-mode="isDevMode"
      :keep-code-in-app-model="keepCodeInAppModel"
      :cell-id="cellId!"
      :cell-type="cellType!"
      :currently-executing-cell="currentlyExecutingCell || ''"
      :is-code-running="isCodeRunning"
    />
    <slot v-if="!isDevMode && keepCodeInAppModel" name="header-title"></slot>
    <v-spacer v-else></v-spacer>

    <v-defaults-provider
      :defaults="{
        VIcon: {
          color: 'bluegrey',
        },
        VBtn: {
          variant: 'text',
          size: 'small',
        },
      }"
    >
      <CellActionButtons
        :is-dev-mode="isDevMode"
        :cell-type="cellType!"
        :cell-id="cellId!"
        :cell-name="cellNameValue"
        @save="$emit('save')"
        @play="$emit('play')"
      />

      <CellMenu
        v-if="isDevMode"
        v-model:is-open="isMenuOpen"
        :cell-id="cellId!"
        :cell-type="cellType!"
        :hide-cell="hideCell"
        :hide-code="hideCode"
        :expand-code="expandCode"
        :non-reactive="nonReactive"
        :show-table="showTable"
        :keep-code-in-app-model="keepCodeInAppModel"
        @update:hide-cell="updateHideCell"
        @update:hide-code="handleHideCode"
        @update:expand-code="handleExpandCode"
        @update:non-reactive="handleReactivity"
        @update:show-table="handleShowTable"
        @delete="$emit('delete')"
      />
    </v-defaults-provider>
  </header>
</template>

<script setup lang="ts">
import { watch } from 'vue';
import { useCellHeader } from '@/composables/CellComponent/cell-header';
import CellNameEditor from './CellNameEditor.vue';
import CellActionButtons from './CellActionButtons.vue';
import CellMenu from './CellMenu.vue';
import { Celltype } from '@/types/notebook'; // Ensure proper import

const props = defineProps({
  isDevMode: Boolean,
  cellType: { type: String as () => Celltype, required: true }, // Ensure Celltype conformity
  cellId: { type: String, required: true },
  hideCell: Boolean,
  hideCode: Boolean,
  expandCode: Boolean,
  nonReactive: Boolean,
  showTable: Boolean,
  cellName: { type: String, default: '' }, // Default for optional props
  currentlyExecutingCell: { type: String, default: '' },
  isCodeRunning: Boolean,
  isFocused: Boolean,
  showHeader: Boolean,
  error: Boolean,
});

const emit = defineEmits([
  'delete',
  'play',
  'save',
  'expandCodeUpdate',
  'updateReactivity',
  'updateShowTable',
  'hideCode',
  'updateHeader',
]);

const {
  isMenuOpen,
  cellNameValue,
  cellTypeColor,
  cellTypeIcon,
  keepCodeInAppModel,
  updateHideCell,
  handleHideCode,
  handleExpandCode,
  handleReactivity,
  handleShowTable,
} = useCellHeader(props, emit);

watch(
  () => props.isFocused,
  (newValue) => {
    if (!newValue) {
      emit('updateHeader', false);
    }
  },
  { immediate: true }
);
</script>

<style lang="scss" scoped>
@import '@/styles/cell.scss';
</style>