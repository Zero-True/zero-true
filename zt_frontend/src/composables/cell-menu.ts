import { ref, watch } from 'vue';
import axios from 'axios';
import { ztAliases } from "@/iconsets/ztIcon";
import type { HideCellRequest } from '@/types/hide_cell_request';
import type { HideCodeRequest } from '@/types/hide_code_request';
import type { ExpandCodeRequest } from '@/types/expand_code_request';
import type { CellReactivityRequest } from '@/types/cell_reactivity_request';
import type { ShowTableRequest } from '@/types/show_table_request';

export interface CellMenuProps {
  cellId: string;
  cellType: string;
  hideCell: boolean;
  hideCode: boolean;
  expandCode: boolean;
  nonReactive: boolean;
  showTable: boolean;
  keepCodeInAppModel: boolean;
}

export function useCellMenu(props: CellMenuProps, emit: any) {
  // Menu state
  const isOpen = ref(false);

  // Two-way binding for all switches
  const hideCell = ref(props.hideCell);
  const hideCode = ref(props.hideCode);
  const expandCode = ref(props.expandCode);
  const nonReactive = ref(props.nonReactive);
  const showTable = ref(props.showTable);

  // API update functions
  const updateHideCell = async (value: boolean | null) => {
    const boolValue = value ?? false;
    const request: HideCellRequest = {
      cellId: props.cellId,
      hideCell: boolValue,
    };
    await axios.post(import.meta.env.VITE_BACKEND_URL + "api/hide_cell", request);
    emit('update:hideCell', boolValue);
  };

  const updateHideCode = async (value: boolean | null) => {
    const boolValue = value ?? false;
    const request: HideCodeRequest = {
      cellId: props.cellId,
      hideCode: boolValue,
    };
    await axios.post(import.meta.env.VITE_BACKEND_URL + "api/hide_code", request);
    emit('update:hideCode', boolValue);
  };

  const updateExpandCode = async (value: boolean | null) => {
    const boolValue = value ?? false;
    const request: ExpandCodeRequest = {
      cellId: props.cellId,
      expandCode: boolValue,
    };
    await axios.post(import.meta.env.VITE_BACKEND_URL + "api/expand_code", request);
    emit('update:expandCode', boolValue);
  };

  const updateReactivity = async (value: boolean | null) => {
    const boolValue = value ?? false;
    const request: CellReactivityRequest = {
      cellId: props.cellId,
      nonReactive: boolValue,
    };
    await axios.post(import.meta.env.VITE_BACKEND_URL + "api/cell_reactivity", request);
    emit('update:nonReactive', value);
  };

  const updateShowTable = async (value: boolean | null) => {
    const boolValue = value ?? false;
    const request: ShowTableRequest = {
      cellId: props.cellId,
      showTable: boolValue,
    };
    await axios.post(import.meta.env.VITE_BACKEND_URL + "api/show_table", request);
    emit('update:showTable', boolValue);
  };

  // Watch for prop changes
  watch(() => props.hideCell, (val) => hideCell.value = val);
  watch(() => props.hideCode, (val) => hideCode.value = val);
  watch(() => props.expandCode, (val) => expandCode.value = val);
  watch(() => props.nonReactive, (val) => nonReactive.value = val);
  watch(() => props.showTable, (val) => showTable.value = val);

  // Emit isOpen changes
  watch(isOpen, (val) => emit('update:isOpen', val));

  return {
    // Icons
    ztAliases,
    // State
    isOpen,
    hideCell,
    hideCode,
    expandCode,
    nonReactive,
    showTable,
    // Actions
    updateHideCell,
    updateHideCode,
    updateExpandCode,
    updateReactivity,
    updateShowTable
  };
}