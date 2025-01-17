import { ref, computed } from 'vue';
import axios from 'axios';
import { useCellType } from './cell-type';

export function useCellHeader(props: any, emit: any) {
  // Create refs for useCellType
  const cellTypeRef = ref(props.cellType);
  const errorRef = ref(props.error);

  // Use your existing composable
  const { cellTypeColor, cellTypeIcon } = useCellType(cellTypeRef, errorRef);

  // State
  const isMenuOpen = ref(false);
  const cellNameValue = ref(props.cellName || props.cellType);

  // Computed
  const keepCodeInAppModel = computed(() => 
    props.cellType === "code" || props.cellType === "sql"
  );

  // API handlers
  const updateHideCell = async (value: boolean) => {
    await axios.post(import.meta.env.VITE_BACKEND_URL + "api/hide_cell", {
      cellId: props.cellId,
      hideCell: value,
    });
  };

  const handleHideCode = async (value: boolean) => {
    await axios.post(import.meta.env.VITE_BACKEND_URL + "api/hide_code", {
      cellId: props.cellId,
      hideCode: value,
    });
    emit("hideCode", value);
  };

  const handleExpandCode = async (value: boolean) => {
    await axios.post(import.meta.env.VITE_BACKEND_URL + "api/expand_code", {
      cellId: props.cellId,
      expandCode: value,
    });
    emit("expandCodeUpdate", value);
  };

  const handleReactivity = async (value: boolean) => {
    await axios.post(import.meta.env.VITE_BACKEND_URL + "api/cell_reactivity", {
      cellId: props.cellId,
      nonReactive: value,
    });
    emit("updateReactivity", value);
  };

  const handleShowTable = async (value: boolean) => {
    await axios.post(import.meta.env.VITE_BACKEND_URL + "api/show_table", {
      cellId: props.cellId,
      showTable: value,
    });
    emit("updateShowTable", value);
  };

  return {
    // State
    isMenuOpen,
    cellNameValue,
    // From useCellType
    cellTypeColor,
    cellTypeIcon,
    // Computed
    keepCodeInAppModel,
    // Actions
    updateHideCell,
    handleHideCode,
    handleExpandCode,
    handleReactivity,
    handleShowTable,
  };
}
