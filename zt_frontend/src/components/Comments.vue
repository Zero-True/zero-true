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
    </div> 
  </v-card>
</template>

<script lang="ts" setup>
import { shallowRef } from 'vue'
const resolvedMode = shallowRef(false)
</script>

<style lang="scss" scoped>
.card {
  position: sticky; top: 100px;
}
</style>
