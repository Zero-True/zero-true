<template>
  <p
    class="mb-4 font-weight-bold"
    :style="{ 'color': cellTypeColor }"
  >Python Cell #1</p>
  <div class="messages">
    <div class="message mb-4">
      <div class="d-flex align-center">
        <h3 class="message__user mr-2">Paris</h3>
        <p class="message__timestamp">1 day ago</p>
      </div>
      <p class="message__content">Lorem ipsum and long text goes here Lorem ipsum and long text goes here</p>
    </div>
    <div class="message mb-4 d-flex">
      <v-divider class="indicator" vertical color="bluegrey" :thickness="1"></v-divider>
      <div class="ml-6">
        <div class="d-flex align-center">
          <h3 class="message__user mr-2">Paris</h3>
          <p class="message__timestamp">1 day ago</p>
        </div>
        <p class="message__content">Lorem ipsum and long text goes here Lorem ipsum and long text goes here</p>
      </div>
    </div>
    <div class="text-box">
      <v-textarea
        variant="outlined" 
      ></v-textarea>
      <div class="d-flex justify-end">
        <v-btn variant="text">Cancel</v-btn>
        <v-btn color="primary" class="ml-2">Submit</v-btn>
      </div>
    </div>
    
    <v-btn
      variant="text"
      slim
    >Reply</v-btn>
  </div> 
</template>

<script setup lang="ts">
import { PropType, toRef } from 'vue'
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
.cell-name {
  position: sticky; top: 100px;
}

.message {
  &__timestamp {
    font-size: .75rem;
    color: rgba(var(--v-theme-bluegrey))
  }
}
</style>
