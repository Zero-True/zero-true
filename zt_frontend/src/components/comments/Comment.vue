<template>
  <p
    class="mb-4 font-weight-bold"
    :style="{ 'color': cellTypeColor }"
  >{{ comment.cell.cellName }}</p>
  <div class="messages">
    <div class="message mb-4">
      <div class="d-flex align-center">
        <h3 class="message__user mr-2">{{ comment.userName }}</h3>
        <p class="message__timestamp">{{ comment.date }}</p>
      </div>
      <p class="message__content">{{ comment.comment }}</p>
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
    <div class="text-box" v-if="showReplyBox">
      <v-textarea
        variant="outlined" 
      ></v-textarea>
      <div class="d-flex justify-end">
        <v-btn variant="text">Cancel</v-btn>
        <v-btn color="primary" class="ml-2">Submit</v-btn>
      </div>
    </div>
    
    <v-btn
      v-if="!showReplyBox"
      variant="text"
      slim
      @click="showReplyBox=true"
    >Reply</v-btn>
  </div> 
</template>

<script setup lang="ts">
import { Celltype } from '@/types/create_request';
import { Comment } from '@/types/comment';
import { useCellTypeColor } from '@/composables/cell-type-color';

import { useCommentsStore } from '@/stores/comments'

const commentsStore = useCommentsStore();

const props = defineProps({
  comment: {
    type: Object as PropType<Comment>,
    required: true,
  },
})

const { cellTypeColor } = useCellTypeColor(toRef(props.comment.cell.cellType))

const showReplyBox = shallowRef(false)
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
