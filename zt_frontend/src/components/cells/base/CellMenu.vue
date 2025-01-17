<template>
  <v-menu :close-on-content-click="false" v-model="isOpen">
    <template v-slot:activator="{ props }">
      <v-btn
        :icon="`ztIcon:${ztAliases.more}`"
        :id="'cellToolbar' + cellId"
        v-bind="props"
      ></v-btn>
    </template>
    
    <v-list bg-color="bluegrey-darken-4">
      <v-list-item v-if="keepCodeInAppModel" :id="'updateCellReactivity' + cellId">
        <template v-slot:prepend>
          <v-switch
            v-model="nonReactive"
            @update:modelValue="updateReactivity"
          ></v-switch>
        </template>
        <v-list-item-title>Non-Reactive</v-list-item-title>
      </v-list-item>

      <v-list-item :id="'hideCell' + cellId">
        <template v-slot:prepend>
          <v-switch
            v-model="hideCell"
            @update:modelValue="updateHideCell"
            :id="'hideCellSwitch' + cellId"
          ></v-switch>
        </template>
        <v-list-item-title>Hide Cell</v-list-item-title>
      </v-list-item>

      <v-list-item v-if="keepCodeInAppModel" :id="'expandCode' + cellId">
        <template v-slot:prepend>
          <v-switch
            v-model="hideCode"
            @update:modelValue="updateHideCode"
          ></v-switch>
        </template>
        <v-list-item-title>Hide Code</v-list-item-title>
      </v-list-item>

      <v-list-item v-if="keepCodeInAppModel" :id="'expandCode' + cellId">
        <template v-slot:prepend>
          <v-switch
            v-model="expandCode"
            @update:modelValue="updateExpandCode"
          ></v-switch>
        </template>
        <v-list-item-title>Expand Code</v-list-item-title>
      </v-list-item>

      <v-list-item v-if="cellType === 'sql'" :id="'updateShowTable' + cellId">
        <template v-slot:prepend>
          <v-switch
            v-model="showTable"
            @update:modelValue="updateShowTable"
          ></v-switch>
        </template>
        <v-list-item-title>Show Table</v-list-item-title>
      </v-list-item>

      <v-list-item
        base-color="error"
        :id="'deleteCell' + cellId"
        class="delete-cell"
        @click="$emit('delete')"
      >
        <template v-slot:prepend>
          <v-icon :icon="`ztIcon:${ztAliases.delete}`"></v-icon>
        </template>
        <v-list-item-title>Delete Cell</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-menu>
</template> 

<script setup lang="ts">
import { useCellMenu, CellMenuProps } from '@/composables/CellComponent/cell-menu';

const props = defineProps({
  cellId: String,
  cellType: String,
  hideCell: Boolean,
  hideCode: Boolean,
  expandCode: Boolean,
  nonReactive: Boolean,
  showTable: Boolean,
  keepCodeInAppModel: Boolean
});

const emit = defineEmits([
  'delete',
  'update:hideCell',
  'update:hideCode',
  'update:expandCode',
  'update:nonReactive',
  'update:showTable',
  'update:isOpen'
]);

const {
  ztAliases,
  isOpen,
  hideCell,
  hideCode,
  expandCode,
  nonReactive,
  showTable,
  updateHideCell,
  updateHideCode,
  updateExpandCode,
  updateReactivity,
  updateShowTable
} = useCellMenu(props as CellMenuProps, emit);
</script>
<style lang="scss" scoped>
@import '@/styles/cell.scss';
</style>