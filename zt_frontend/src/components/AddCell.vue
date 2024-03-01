<template>
  <v-menu transition="scale-transition">
    <template v-slot:activator="{ props }">
      <div v-bind="props" class="activator-area">
        <div class="divider">
          <v-divider class="divider__divider-line" color="bluegrey-darken-2"></v-divider>
          <v-btn :prepend-icon="`ztIcon:${ztAliases.circleAdd}`" variant="plain" density="compact" :ripple="false"
            class="divider__btn bg-background">Add cell</v-btn>
        </div>
      </div>
    </template>
    <v-list bg-color="bluegrey-darken-4">
      <v-list-item v-for="(item, i) in addCellItems" :key="i" class="add-cell-item"
        v-bind="cellId ? { id: 'addCell_' + item.title + '_' + cellId } : {}" @click="$emit('createCodeCell', item.cellType)">
        <template v-slot:prepend>
          <v-icon :icon="item.icon"></v-icon>
        </template>
        <v-list-item-title>{{ item.title }}</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-menu>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { ztAliases } from '@/iconsets/ztIcon'
import { Celltype } from '@/types/create_request';

defineProps({
  onClick: null,
  cellId: String
})

defineEmits<{
  (e: 'createCodeCell', cellType: Celltype): void
}>()

const addCellItems = ref<{
  title: string;
  cellType: Celltype,
  icon: string
}[]>([
  { title: 'Code', cellType: 'code', icon: `ztIcon:${ztAliases.code}` },
  { title: 'SQL', cellType: 'sql', icon: `ztIcon:${ztAliases.sql}` },
  { title: 'Markdown', cellType: 'markdown', icon: `ztIcon:${ztAliases.markdown}` },
  { title: 'Text', cellType: 'text', icon: `ztIcon:${ztAliases.text}` },
])
</script>
<style lang="scss" scoped>
.divider {
  position: relative;
  height: 24px;

  &__divider-line {
    position: absolute;
    top: 50%;
    width: 100%;
    transform: translateY(-50%);
  }

  &__btn {
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    opacity: 1;
  }
}

.divider:hover {
  cursor: pointer;
}

.divider:hover .divider__divider-line {
  background-color: white;
}

.divider:hover .divider__btn {
  color: white !important;
}
</style>