<template>
  <div class="messages">
    <div class="message mb-4">
      <div class="d-flex justify-space-between align-start">
        <CommentTextarea
          v-if="editingCommentId === comment.id"
          v-model="editingCommentChange"
          :isSaving="savingEdit"
          @cancel="cancelEdit"
          @submit="submitEditChange(comment.cell.cellId ?? '')"
        />
        <p v-else class="message__content">{{ comment.comment }}</p>
        <div class="d-flex align-center">
          <v-btn
            v-if="!comment.resolved && !editingCommentId"
            icon="$success"
            variant="plain"
            :ripple="false"
            @click="() => resolveComment(comment.id, comment.cell.cellId ?? '')"
          ></v-btn>
          <CommentMenu
            v-if="!editingCommentId"
            @editComment="
              () => {
                if (!comment.resolved) {
                  edit(comment);
                }
              }
            "
            @deleteComment="
              () => deleteComment(comment.id, comment.cell.cellId ?? '')
            "
          />
        </div>
      </div>

      <div class="d-flex align-center">
        <!-- <h3 class="message__user mr-2">{{ comment.userName }}</h3> -->
        <p class="message__timestamp">{{ comment.date }}</p>
      </div>
    </div>
    <div class="message mb-4 d-flex" v-for="reply in comment.replies">
      <v-divider
        class="indicator"
        vertical
        color="bluegrey"
        :thickness="1"
      ></v-divider>
      <div class="ml-6 flex-1-1">
        <div class="d-flex justify-space-between align-start">
          <CommentTextarea
            v-if="editingCommentId === reply.id"
            v-model="editingCommentChange"
            :isSaving="savingEdit"
            @cancel="cancelEdit"
            @submit="
              () => submitEditChange(comment.cell.cellId ?? '', comment.id)
            "
          />
          <p v-else class="message__content">{{ reply.comment }}</p>
          <div class="d-flex align-center">
            <div>
              <CommentMenu
                v-if="!editingCommentId"
                @editComment="
                  () => {
                    if (!comment.resolved) {
                      edit(reply);
                    }
                  }
                "
                @deleteComment="
                  () =>
                    deleteComment(
                      reply.id,
                      comment.cell.cellId ?? '',
                      comment.id
                    )
                "
              />
            </div>
          </div>
        </div>
        <div class="d-flex align-center">
          <!-- <h3 class="message__user mr-2">{{ reply.userName }}</h3> -->
          <p class="message__timestamp">{{ reply.date }}</p>
        </div>
      </div>
    </div>
    <div class="text-box" v-if="showReplyBox">
      <CommentTextarea
        v-model="newCommentText"
        :is-saving="savingReply"
        @cancel="
          () => {
            commentsStore.editorAvailable = true;
            showReplyBox = false;
          }
        "
        @submit="submitNewReply"
      />
    </div>
    <v-btn
      v-if="!showReplyBox && !comment.resolved"
      variant="text"
      slim
      :disabled="!commentsStore.editorAvailable"
      @click="
        () => {
          commentsStore.editorAvailable = false;
          showReplyBox = true;
        }
      "
      >Reply</v-btn
    >
  </div>
</template>

<script setup lang="ts">
import { Comment } from "@/static-types/comment";
import CommentMenu from "./CommentMenu.vue";
import CommentTextarea from "./CommentTextarea.vue";
import { useCommentsStore } from "@/stores/comments";
import { v4 as uuidv4 } from "uuid";

const commentsStore = useCommentsStore();

const props = defineProps({
  comment: {
    type: Object as PropType<Comment>,
    required: true,
  },
});

const newCommentText = shallowRef("");
const showReplyBox = shallowRef(false);
const savingReply = shallowRef(false);

// Edit
const editingCommentId = shallowRef<string | undefined>(undefined);
const editingCommentChange = shallowRef("");
const savingEdit = shallowRef(false);

function edit(comment: Comment) {
  commentsStore.editorAvailable = false;
  editingCommentId.value = comment.id;
  editingCommentChange.value = comment.comment;
}

function cancelEdit() {
  commentsStore.editorAvailable = true;
  editingCommentId.value = undefined;
}
async function submitEditChange(cellId: string, parentCommentId?: string) {
  if (editingCommentId.value) {
    savingEdit.value = true;
    await commentsStore.editComment(
      editingCommentId.value,
      cellId,
      editingCommentChange.value,
      parentCommentId
    );
    savingEdit.value = false;
    editingCommentId.value = undefined;
    editingCommentChange.value = "";
    commentsStore.editorAvailable = true;
  }
}

// DELETE
async function deleteComment(
  id: string,
  cellId: string,
  parentCommentId?: string
) {
  await commentsStore.deleteComment(id, cellId, parentCommentId);
}

async function submitNewReply() {
  savingReply.value = true;
  const options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  };
  const date = Intl.DateTimeFormat("en-US", options).format(new Date());
  const newReply = {
    id: uuidv4(),
    cell: props.comment.cell,
    userName: "",
    date: date,
    comment: newCommentText.value,
    replies: [],
    resolved: false,
  };

  await commentsStore.replyComment(props.comment.id, newReply);
  savingReply.value = false;
  newCommentText.value = "";
  showReplyBox.value = false;
  commentsStore.editorAvailable = true;
}

async function resolveComment(id: string, cellId: string) {
  await commentsStore.resolveComment(id, cellId);
}
</script>

<style lang="scss" scoped>
.cell-name {
  position: sticky;
  top: 100px;
}

.message {
  padding-top: 10px;
  &__timestamp {
    font-size: 0.75rem;
    color: rgba(var(--v-theme-bluegrey));
  }
  &__content {
    font-size: 14px;
    word-break: break-word;
  }
}

.comment__actions {
  position: absolute;
  right: 0;
}
</style>
