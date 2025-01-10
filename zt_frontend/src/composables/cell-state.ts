import { ref, watch, Ref } from "vue";

export function useCellState(hideCell: Ref<boolean>, nonReactive: Ref<boolean>) {
  const showHeader = ref(false);
  const hideCellValue = ref(hideCell.value);
  const nonReactiveValue = ref(nonReactive.value);

  watch(hideCell, (newValue) => {
    hideCellValue.value = newValue;
  });

  watch(nonReactive, (newValue) => {
    nonReactiveValue.value = newValue;
  });

  return {
    showHeader,
    hideCellValue,
    nonReactiveValue,
  };
}
