import { ref, shallowRef } from 'vue';
import { defineStore } from 'pinia';
import { Celltype } from '@/types/notebook';

export interface Comment {
  cellId: string;
  cellName: string;
  cellType: Celltype;
  userName: string;
  date: string;
  comment: string;
  replies: Comment[];
  resolved: boolean;
}

export const useCommentsStore = defineStore('comments', () => {
  // States 
  const showComments = shallowRef(false);
  const comments = ref<Comment[]>([]);

  // Getters
  // Actions
  function toggleComments() {
    showComments.value = !showComments.value;
  }

  return {
    // States
    showComments,
    comments,
    // Actions
    toggleComments
  }
});
