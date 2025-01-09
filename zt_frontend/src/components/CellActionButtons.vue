<template>
  <div class="actions">
    <v-btn
      v-if="isDevMode && showSaveBtn"
      :icon="`ztIcon:${ztAliases.save}`"
      @click="$emit('save')"
    ></v-btn>

    <v-btn
      v-if="isDevMode && showPlayBtn"
      :id="'runCode' + cellId"
      :icon="`ztIcon:${ztAliases.play}`"
      @click="$emit('play')"
    ></v-btn>
    
    <v-btn
      v-if="commentsEnabled"
      :class="[{ 'message-btn--alert': numberOfComments }]"
      @click="showComments"
      :ripple="false"
      slim
      rounded="circle"
    >
      <template #default>
        <v-icon
          v-if="numberOfComments === 0"
          size="x-large"
          :icon="`ztIcon:${ztAliases.message}`"
        ></v-icon>
        <span v-else class="text-primary message-btn__counter">{{
          numberOfComments
        }}</span>
      </template>
    </v-btn>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { ztAliases } from "@/iconsets/ztIcon";
import { globalState } from "@/global_vars";
import { useCommentsStore } from "@/stores/comments";
import { storeToRefs } from "pinia";
import { Celltype } from "@/types/notebook"; // Import the correct Celltype

// Define props with stricter type constraints
const props = defineProps({
  isDevMode: { type: Boolean, required: true },
  cellType: { type: String as () => Celltype, required: true }, // Celltype validation
  cellId: { type: String, required: true },
  cellName: { type: String, required: true },
});

// Define emitted events
const emit = defineEmits(['save', 'play']);

// Store reference
const commentsStore = useCommentsStore();
const { commentsByCell } = storeToRefs(commentsStore);

// Computed properties
const numberOfComments = computed(() => commentsByCell.value(props.cellId));
const showPlayBtn = computed(() => props.cellType === "code" || props.cellType === "sql");
const showSaveBtn = computed(() => props.cellType === "markdown" || props.cellType === "text");
const commentsEnabled = computed(() => globalState.comments_enabled);

// Function to show comments
const showComments = () => {
  commentsStore.showCommentsPerCell({
    cellId: props.cellId,
    cellName: props.cellName,
    cellType: props.cellType as Celltype,
  });
};
</script>

<style lang="scss" scoped>
@import '@/styles/cell.scss';
</style>