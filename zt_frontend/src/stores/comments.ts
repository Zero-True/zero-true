import { Cell, Comment } from '@/types/comment';

export const useCommentsStore = defineStore('comments', () => {
  // States 
  const showComments = shallowRef(false);
  const allComments = ref<Comment[]>([]);
  const selectedCell = ref<Cell>();

  // Getters
  const displayedComments = computed(() => {
    if (!selectedCell.value) return allComments.value
    const result = allComments.value.filter(c => c.cell.cellId === selectedCell.value?.cellId)
    return result ?? []
  });

  // Actions
  async function addComment(comment: Comment) {
    await new Promise(resolve => setTimeout(resolve, 800))
    allComments.value.push(comment);
  }

  async function replyComment(replyToCommentId: string, comment: Comment) {
    await new Promise(resolve => setTimeout(resolve, 800))
    const commentReplyTo = allComments.value.find(c => c.commentId === replyToCommentId);
    commentReplyTo?.replies.push(comment);
  }

  function closeComments() {
    showComments.value = false;
  }
  function showAllComments() {
    showComments.value = true;
  }
  
  function showCommentsPerCell(cell: Cell) {
    showComments.value = true;
    selectedCell.value = cell;
  }

  return {
    // States
    showComments,
    allComments,
    selectedCell,
    // Getters,
    displayedComments,
    // Actions
    addComment,
    replyComment,
    closeComments,
    showAllComments,
    showCommentsPerCell
  }
});
