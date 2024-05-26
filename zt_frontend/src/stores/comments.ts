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
  
  async function deleteComment(id: string, parentCommentId?: string) {
    await new Promise(resolve => setTimeout(resolve, 800))
    if (parentCommentId) {
      const parentComment = allComments.value.find(c => c.id === parentCommentId)
      if (parentComment) {
        parentComment.replies = parentComment.replies.filter(r => r.id !== id)
      } 
    } else {
      allComments.value = allComments.value.filter(c => c.id !== id)
    }
  }

  async function editComment(commentId: string, newCommentText: string, parentCommentId?: string) {
    await new Promise(resolve => setTimeout(resolve, 800))
    const editingComment = allComments.value.find(c => c.id === (parentCommentId ?? commentId));
    if (parentCommentId) {
      const editingReply = editingComment?.replies.find(r => r.id === commentId)
      editingReply && (editingReply.comment = newCommentText)
    } else {
      editingComment && (editingComment.comment = newCommentText)
    }
  }

  async function replyComment(replyToCommentId: string, comment: Comment) {
    await new Promise(resolve => setTimeout(resolve, 800))
    const commentReplyTo = allComments.value.find(c => c.id === replyToCommentId);
    commentReplyTo?.replies.push(comment);
  }

  async function resolveComment(id: string) {
    console.log('resolveComment', id)
    await new Promise(resolve => setTimeout(resolve, 200))
    const resolveComment = allComments.value.find(c => c.id === id);
    if (resolveComment) resolveComment.resolved = true;
  }

  function closeComments() {
    showComments.value = false;
    selectedCell.value = undefined;
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
    editComment,
    deleteComment,
    replyComment,
    closeComments,
    resolveComment,
    showAllComments,
    showCommentsPerCell
  }
});
