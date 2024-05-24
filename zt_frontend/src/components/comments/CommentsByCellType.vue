<template>
  <h1>HERE</h1> 
</template>

<script setup lang="ts">
import { PropType, shallowRef, toRef } from 'vue'
import { Celltype } from '@/types/create_request';
import { useCellTypeColor } from '@/composables/cell-type-color';


const props = defineProps({
  cellType: {
    type: String as PropType<Celltype>,
    default: 'code', 
  },
  cellName: {
    type: String,
    default: null
  }
})

const { cellTypeColor } = useCellTypeColor(toRef(props.cellType))

</script>

<style lang="scss" scoped>
.card {
  position: sticky; top: 100px;
}
</style>
