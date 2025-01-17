<template>
  <v-card
    v-if="isDevMode || (!isDevMode && !hideCellValue)"
    :id="'codeCard' + cellId"
    :class="['cell', { 'cell--dev': isDevMode }]"
    color="bluegrey-darken-4"
    width="100%"
    @mouseenter="showHeader = true"
    @mouseleave="showHeader = false"
  >
    <v-divider
      class="indicator"
      vertical
      :color="dividerColor"
      :thickness="4"
    ></v-divider>
    <div class="content">
      <CellHeader
        :is-dev-mode="isDevMode"
        :cell-type="cellType"
        :cell-id="cellId"
        :hide-cell="hideCell"
        :hide-code="hideCode"
        :expand-code="expandCode"
        :non-reactive="nonReactive"
        :show-table="showTable"
        :cell-name="cellName"
        :currently-executing-cell="currentlyExecutingCell"
        :is-code-running="isCodeRunning"
        :is-focused="isFocused"
        :show-header="showHeader"
        @delete="$emit('delete')"
        @play="$emit('play')"
        @save="$emit('save')"
        @expand-code-update="$emit('expandCodeUpdate', $event)"
        @update-reactivity="$emit('updateReactivity', $event)"
        @update-show-table="$emit('updateShowTable', $event)"
        @hide-code="$emit('hideCode', $event)"
        @rename-cell="$emit('renameCell', $event)"
        @update-header="showHeader = $event"
      >
        <template #header-title>
          <slot name="header-title"></slot>
        </template>
      </CellHeader>
      
      <div
        :class="['code', { 'code--dev': isDevMode }]"
        v-if="isDevMode || (!isDevMode && keepCodeInAppModel)"
      >
        <slot name="code"></slot>
      </div>
      <div
        :class="['outcome', { 'outcome--dev': isDevMode }]"
        v-if="!(isDevMode && !isAppRoute && cellType === 'text') && cellHasOutput"
      >
        <slot name="outcome"></slot>
      </div>
    </div>
    <v-tooltip v-if="nonReactiveValue" text="Cell is Stale">
      <template v-slot:activator="{ props }">
        <v-divider
          v-bind="props"
          class="indicator"
          vertical
          color="warning"
          :thickness="8"
        />
      </template>
    </v-tooltip>
  </v-card>
  <add-cell
    v-if="isDevMode"
    :cell-id="cellId"
    @createCodeCell="(e) => $emit('addCell', e)"
  />
</template>
<script setup lang="ts">
import { computed, PropType, toRef } from "vue";
import type { Celltype } from "@/types/create_request";
import AddCell from "./AddCell.vue";
import CellHeader from "./CellHeader.vue";
import { useCellType } from "@/composables/CellComponent/cell-type";
import { useCellState } from "@/composables/CellComponent/cell-state";
import { useRouteHelpers } from "@/composables/CellComponent/route-helpers";

const props = defineProps({
  isDevMode: Boolean,
  cellType: {
    type: String as PropType<Celltype>,
    default: "code",
  },
  cellId: {
    type: String,
    required: true,
  },
  error: Boolean,
  hideCell: {
    type: Boolean,
    default: false,
  },
  hideCode: {
    type: Boolean,
    default: false,
  },
  expandCode: {
    type: Boolean,
    default: false,
  },
  nonReactive: {
    type: Boolean,
    default: false,
  },
  showTable: {
    type: Boolean,
    default: false,
  },
  cellName: {
    type: String,
    default: null,
  },
  currentlyExecutingCell: {
    type: String,
    default: null,
  },
  isCodeRunning: {
    type: Boolean,
    default: false,
  },
  cellHasOutput: {
    type: Boolean,
    default: false,
  },
  isFocused: {
    type: Boolean,
    default: false,
  },
});

const emits = defineEmits<{
  (e: "delete"): void;
  (e: "play"): void;
  (e: "save"): void;
  (e: "expandCodeUpdate", expand: Boolean): void;
  (e: "updateReactivity", expand: Boolean): void;
  (e: "updateShowTable", expand: Boolean): void;
  (e: "hideCode", hideCode: Boolean): void;
  (e: "addCell", cellType: Celltype): void;
  (e: "renameCell", cellName: String): void;
}>();

// Composables
const { cellTypeColor: dividerColor } = useCellType(toRef(props.cellType), toRef(props.error));
const { showHeader, hideCellValue, nonReactiveValue } = useCellState(
  toRef(props.hideCell),
  toRef(props.nonReactive)
);
const { isAppRoute } = useRouteHelpers();

const keepCodeInAppModel = computed(() => props.cellType === "code" || props.cellType === "sql");
</script>

<style lang="scss" scoped>
@import '@/styles/cell.scss';
</style>