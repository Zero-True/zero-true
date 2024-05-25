<template>
   <v-menu :close-on-content-click="false">
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
      <v-list-item @click="editComment">
        <template v-slot:prepend>
          <v-icon :icon="`ztIcon:${ztAliases.edit}`"></v-icon>
        </template>
        <v-list-item-title>Edit</v-list-item-title>
      </v-list-item>
      <v-list-item base-color="error" @click="deleteComment">
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
function deleteComment () {}

function editComment () {}
</script>

<style lang="scss" scoped>
</style>
