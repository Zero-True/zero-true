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
        <CommentsPerCell />
      </div> 

      <v-btn
        :prepend-icon="`ztIcon:${ztAliases.circleAdd}`"
        variant="outlined"
        class="w-100 add-comment-btn" 
      >Add Comment</v-btn>
    </div> 
  </v-card>
</template>

<script setup lang="ts">
import { shallowRef } from 'vue'
import { ztAliases } from '@/iconsets/ztIcon'
import CommentsPerCell from './CommentsPerCell.vue'

const resolvedMode = shallowRef(false)
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
