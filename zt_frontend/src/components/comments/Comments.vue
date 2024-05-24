<template>
  <v-card title="Comments" class="card">
    <div class="content pa-4">
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
        <CommentsByCellType />
      </div> 
    </div> 
  </v-card>
</template>

<script setup lang="ts">
import { shallowRef } from 'vue'
import CommentsByCellType from './CommentsByCellType.vue'

const resolvedMode = shallowRef(false)
</script>

<style lang="scss" scoped>
.card {
  position: sticky; top: 100px;
}
</style>
