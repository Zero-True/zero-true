<template>
  <v-menu transition="scale-transition" minWidth="0" target="cursor">
    <template v-slot:activator="{ props }">
      <div v-bind="cellId ? { ...props, id: 'addCell' + cellId } : props" class="activator-area-push">
        <div class="divider-container">
          <div class="divider">
            <v-divider class="divider__line" color="bluegrey-darken-2"></v-divider>
            <span class="divider__text">
              <v-btn :prepend-icon="`ztIcon:${ztAliases.circleAdd}`" variant="plain" density="compact" :ripple="false"
              class="divider__btn bg-background">Add cell</v-btn>
            </span>
            <v-divider class="divider__line" color="bluegrey-darken-2"></v-divider>
          </div>
        </div>
      </div>
    </template>
    <v-list bg-color="bluegrey-darken-4">
      <v-list-item
        v-for="(item, i) in addCellItems"
        :key="i"
        class="add-cell-item"
        v-bind="cellId ? { id: 'addCell_' + item.title + '_' + cellId } : {}"
        @click="$emit('createCodeCell', item.cellType)"
      >
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
.activator-area-push {
  margin: 0;
  padding: 0;
  height: 2px;
  transition: height 0.2s ease;

  &:hover {
    height: 24px;
  }
}

.divider-container {
  height: 100%;
  opacity: 0;
  transition: opacity 0.2s ease;

  .activator-area-push:hover & {
    opacity: 1;
  }
}

.divider {
  display: flex;
  align-items: center;

  &__line {
    flex: 1;
    background-color: bluegrey-darken-2;
    transition: background-color 0.2s ease;
  }

  &__text {
    display: flex;
    align-items: center;
    margin: 0 8px;
    color: bluegrey-darken-2;
    transition: color 0.2s ease;
  }

  &__icon {
    margin-right: 4px;
  }
}

.divider:hover {
  .divider__btn {
    color: white !important;
  }
}
</style>