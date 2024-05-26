<template>
  <p
    class="mb-4 font-weight-bold"
    :style="{ 'color': cellTypeColor }"
  >{{ comment.cell.cellName }}</p>
  <div class="messages">
    <div class="message mb-4">
      <div class="d-flex align-center justify-space-between">
        <div class="d-flex align-center">
          <h3 class="message__user mr-2">{{ comment.userName }}</h3>
          <p class="message__timestamp">{{ comment.date }}</p>
        </div>
        <div>
          <v-btn
            v-if="!comment.resolved"
            icon="$success"
            variant="plain"
            :ripple="false"
            @click="() => resolveComment(comment.id)" 
          ></v-btn>
          <CommentMenu
            v-if="!editingCommentId && !comment.resolved"
            @editComment="edit(comment)" 
            @deleteComment="() => deleteComment(comment.id)" 
          />
        </div>
      </div>
      <CommentTextarea
        v-if="editingCommentId === comment.id"
        v-model="editingCommentChange" 
        :isSaving="savingEdit" 
        @cancel="cancelEdit" 
        @submit="submitEditChange"
      />
      <p v-else class="message__content">{{ comment.comment }}</p>
    </div>
    <div class="message mb-4 d-flex" v-for="reply in comment.replies">
      <v-divider class="indicator" vertical color="bluegrey" :thickness="1"></v-divider>
      <div class="ml-6 flex-1-1">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center">
            <h3 class="message__user mr-2">{{ reply.userName }}</h3>
            <p class="message__timestamp">{{ reply.date }}</p>
          </div>
          <div>
            <CommentMenu 
              v-if="!editingCommentId"
              @editComment="edit(reply)" 
              @deleteComment="() => deleteComment(reply.id, comment.id)" 
            />
          </div>
        </div>
        <CommentTextarea
          v-if="editingCommentId === reply.id"
          v-model="editingCommentChange"
          :isSaving="savingEdit"
          @cancel="cancelEdit"
          @submit="() => submitEditChange(comment.id)"
        />
        <p v-else class="message__content">{{ reply.comment }}</p>
      </div>
    </div>
    <div class="text-box" v-if="showReplyBox">
      <CommentTextarea
        v-model="newCommentText" 
        :is-saving="savingReply" 
        @cancel="showReplyBox=false"
        @submit="submitNewReply"
      />
    </div>
    
    <v-btn
      v-if="!showReplyBox && !comment.resolved"
      variant="text"
      slim
      @click="showReplyBox=true"
    >Reply</v-btn>
  </div> 
</template>

<script setup lang="ts">
import { Comment } from '@/types/comment';
import { useCellTypeColor } from '@/composables/cell-type-color';
import CommentMenu from './CommentMenu.vue'
import CommentTextarea from './CommentTextarea.vue'
import { useCommentsStore } from '@/stores/comments'

const commentsStore = useCommentsStore();

const props = defineProps({
  comment: {
    type: Object as PropType<Comment>,
    required: true,
  },
})


const { cellTypeColor } = useCellTypeColor(toRef(props.comment.cell.cellType))

const newCommentText = shallowRef('')
const showReplyBox = shallowRef(false)
const savingReply = shallowRef(false)

// Edit
const editingCommentId = shallowRef<string | undefined>(undefined)
const editingCommentChange = shallowRef('')
const savingEdit = shallowRef(false)

function edit(comment: Comment) {
  editingCommentId.value = comment.id;
  editingCommentChange.value = comment.comment;
}

function cancelEdit() {
  editingCommentId.value = undefined
}
async function submitEditChange(parentCommentId?: string) {
  if (editingCommentId.value) {
    savingEdit.value = true;
    await commentsStore.editComment(editingCommentId.value, editingCommentChange.value, parentCommentId);
    savingEdit.value = false;
    editingCommentId.value = undefined
    editingCommentChange.value = ''
  } 
}

// DELETE
async function deleteComment(id: string, parentCommentId?: string) {
  await commentsStore.deleteComment(id, parentCommentId);
}

async function submitNewReply() {
  savingReply.value = true;
  const newReply = {
    id: `${Math.random()}`,
    cell: props.comment.cell,
    userName: 'User 1', 
    date: 'today',
    comment: newCommentText.value,
    replies: [],
    resolved: false,
  };

  await commentsStore.replyComment(props.comment.id, newReply);
  savingReply.value = false;
  newCommentText.value = '';
  showReplyBox.value = false;
}

async function resolveComment(id: string) {
  await commentsStore.resolveComment(id);
}
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
