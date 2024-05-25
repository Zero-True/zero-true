<template>
  <v-card class="card">
    <v-template>
      <div class="d-flex pa-4">
        <h3>Comments</h3>
        <v-btn
          icon="mdi:mdi-close"
          variant="text"
          class="close-btn"
          :ripple="false"
          @click="closeComments()"
        ></v-btn>
      </div> 
    </v-template>
    
    <div class="content ma-4">
      <v-btn-toggle
        v-model="resolvedMode" 
        :border="false"
        mandatory="force"
        color="primary"
        rounded="pill"
      >
        <v-btn :value="false" class="mr-4">Open</v-btn>
        <v-btn :value="true">Resolved</v-btn>
      </v-btn-toggle>
      <div class="mt-6 flex-1-1 ">
        <div class="text-box" v-if="displayAddCommentTextarea">
          <v-textarea
            variant="outlined" 
            v-model="newCommentText"
          ></v-textarea>
          <div class="d-flex justify-end">
            <v-btn variant="text">Cancel</v-btn>
            <v-btn
              color="primary"
              class="ml-2"
              :disabled="!newCommentText || savingNewComment"
              :loading="savingNewComment" 
              @click="submitNewComment()"
            >Submit</v-btn>
          </div>
        </div>
        <div class="empty-state" v-if="!commentsStore.displayedComments.length && !displayAddCommentTextarea">
          <v-icon :icon="`ztIcon:${ztAliases.message}`"/>
          <p>No comments yet</p>
          <p class="empty-state__text mt-2">Add a comment by clicking on the cell you want to add a comment to.</p>
        </div>
        <template v-else>
          <Comment
            v-for="comment in commentsStore.displayedComments"   
            :comment="comment" 
          />
        </template>
      </div> 

      <v-btn
        v-if="commentsStore.selectedCell"
        :prepend-icon="`ztIcon:${ztAliases.circleAdd}`"
        variant="outlined"
        class="w-100 add-comment-btn" 
        @click="displayAddCommentTextarea=!displayAddCommentTextarea"
      >Add Comment</v-btn>
    </div> 
  </v-card>
</template>

<script setup lang="ts">
import { ztAliases } from '@/iconsets/ztIcon'
import Comment from './Comment.vue'

import { useCommentsStore } from '@/stores/comments'

const commentsStore = useCommentsStore();

const { addComment, closeComments } = commentsStore
const { selectedCell } = storeToRefs(commentsStore)

const resolvedMode = shallowRef(false)
const displayAddCommentTextarea = shallowRef(false)
const newCommentText = shallowRef('')
const savingNewComment = shallowRef(false)

watch(selectedCell, () => {
  // Reset component variables
  resolvedMode.value = false
  displayAddCommentTextarea.value = false
  newCommentText.value = ''
  savingNewComment.value = false
})

async function submitNewComment() {
  savingNewComment.value = true
  const newComment = {
    commentId: 1, 
    cell: commentsStore.selectedCell,
    userName: 'Yuchao', 
    date: 'today',
    comment: newCommentText.value,
    replies: [],
    resolved: false,
  };

  await addComment(newComment);
  savingNewComment.value = false;
  newCommentText.value = '';
  displayAddCommentTextarea.value = false;
}
</script>

<style lang="scss" scoped>
.card {
  position: sticky;
  top: 100px;
}
.close-btn {
  position: absolute;
  top: 0;
  right: 0;
}
.content {
  position: relative;
  height: 100%;
  min-height: 700px;
}
.empty-state {
  margin-top: 200px;
  text-align: center;
  &__text {
    max-width: 20em;
    margin: 0 auto;
    line-height: 1.8rem;
    color: rgb(var(--v-theme-bluegrey));
  }
}
.add-comment-btn {
  position: absolute;
  bottom: 0;
}
</style>
