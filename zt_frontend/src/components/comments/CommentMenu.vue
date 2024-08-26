<template>
   <v-menu>
    <template v-slot:activator="{ props }">
      <v-btn
        :icon="`ztIcon:${ztAliases.more}`"
        v-bind="props"
        variant="plain"
        size="small"
      >
      </v-btn>
    </template>
    <v-list bg-color="bluegrey-darken-4">
      <v-list-item :disabled="!commentsStore.editorAvailable" @click="emit('editComment')">
        <template v-slot:prepend>
          <v-icon :icon="`ztIcon:${ztAliases.edit}`"></v-icon>
        </template>
        <v-list-item-title>Edit</v-list-item-title>
      </v-list-item>
      <v-list-item base-color="error" @click="emit('deleteComment')">
        <template v-slot:prepend>
          <v-icon :icon="`ztIcon:${ztAliases.delete}`"></v-icon>
        </template>
        <v-list-item-title>Delete</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script setup lang="ts">
import { ztAliases } from '@/iconsets/ztIcon'
import { useCommentsStore } from '@/stores/comments';

const commentsStore = useCommentsStore();

const emit = defineEmits(['deleteComment', 'editComment'])
</script>

<style lang="scss" scoped>
</style>
