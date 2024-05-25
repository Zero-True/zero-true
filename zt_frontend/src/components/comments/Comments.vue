<template>
  <v-card title="Comments" class="card">
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
      <div class="mt-6">
        <div class="text-box" v-if="!commentsStore.displayedComments.length && displayAddCommentTextarea">
          <v-textarea
            variant="outlined" 
            v-model="newCommentText"
          ></v-textarea>
          <div class="d-flex justify-end">
            <v-btn variant="text">Cancel</v-btn>
            <v-btn
              color="primary"
              class="ml-2"
              @click="submitNewComment()"
            >Submit</v-btn>
          </div>
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

const { addComment } = commentsStore

const resolvedMode = shallowRef(false)
const displayAddCommentTextarea = shallowRef(false)
const newCommentText = shallowRef('')

function submitNewComment() {
  const newComment = {
    commentId: 1, 
    cell: commentsStore.selectedCell,
    userName: 'Yuchao', 
    date: 'today',
    comment: newCommentText.value,
    replies: [],
    resolved: false,
  };

  addComment(newComment);
}
</script>

<style lang="scss" scoped>
.card {
  position: sticky;
  top: 100px;
}
.content {
  position: relative;
  height: 100%;
  min-height: 700px;
}
.add-comment-btn {
  position: absolute;
  bottom: 0;
}
</style>
