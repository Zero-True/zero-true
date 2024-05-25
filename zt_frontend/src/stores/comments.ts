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
    console.log('allComments.value', allComments.value.length) 
    return result ?? []
  });

  // Actions
  function addComment(comment: Comment) {
    allComments.value.push(comment);
  }

  function replyComment(replyToCommentId: string, comment: Comment) {
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
