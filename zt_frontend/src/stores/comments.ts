import {
  Comment as NotebookComment,
  Comments,
  Celltype,
} from "@/types/notebook";
import { Comment, Cell } from "@/static-types/comment";
import { AddCommentRequest } from "@/types/add_comment_request";
import { DeleteCommentRequest } from "@/types/delete_comment_request";
import  { EditCommentRequest } from "@/types/edit_comment_request";
import { ResolveCommentRequest } from "@/types/resolve_comment_request";
import { AddReplyRequest } from "@/types/add_reply_request";
import { DeleteReplyRequest } from "@/types/delete_reply_request";
import { EditReplyRequest } from "@/types/edit_reply_request";
import axios from "axios";

export const useCommentsStore = defineStore("comments", () => {
  // States
  const showComments = shallowRef(false);
  const allComments = ref<Comment[]>([]);
  const selectedCell = ref<Cell>();
  const editorAvailable = ref(true);

  // LoadComments
  function loadComments(
    comments: Comments,
    cellId: string,
    cellType: Celltype,
    cellName: string
  ) {
    const cell = { cellId, cellName, cellType };
    for (const commentId in comments) {
      const replies = [] as Comment[];
      for (const replyId in comments[commentId].replies) {
        const reply = comments[commentId]?.replies?.[replyId];
        replies.push({
          id: replyId,
          cell,
          userName: "",
          date: reply?.date ?? "",
          comment: reply?.comment ?? "",
          replies: [] as Comment[],
          resolved: reply?.resolved ?? false,
        });
      }
      const comment = {
        id: commentId,
        cell,
        userName: "",
        date: comments[commentId].date ?? "",
        comment: comments[commentId].comment ?? "",
        replies,
        resolved: comments[commentId].resolved ?? false,
      };
      allComments.value.push(comment);
    }
  }

  // Getters
  const displayedComments = computed(() => {
    editorAvailable.value = true;
    if (!selectedCell.value) return allComments.value;
    const result = allComments.value.filter(
      (c) => c.cell.cellId === selectedCell.value?.cellId
    );
    return result ?? [];
  });

  const commentsByCell = computed(
    () => (cellId: string) =>
      allComments.value.filter((c) => c.cell.cellId === cellId).length
  );

  // Actions
  async function addComment(comment: Comment) {
    try {
      const addCommentRequest: AddCommentRequest = {
        cellId: comment.cell.cellId ?? "",
        commentId: comment.id,
        comment: comment.comment,
        date: comment.date,
      };
      await axios.post(
        import.meta.env.VITE_BACKEND_URL + "api/add_comment",
        addCommentRequest
      );
      allComments.value.push(comment);
    } catch (error) {
      console.error("Error adding comment:", error);
    }
  }

  async function deleteComment(
    id: string,
    cellId: string,
    parentCommentId?: string
  ) {
    try {
      if (parentCommentId) {
        const parentComment = allComments.value.find(
          (c) => c.id === parentCommentId
        );
        if (parentComment) {
          const deleteReplyRequest: DeleteReplyRequest = {
            cellId: parentComment.cell.cellId ?? "",
            parentCommentId: parentCommentId,
            commentId: id,
          };
          await axios.post(
            import.meta.env.VITE_BACKEND_URL + "api/delete_reply",
            deleteReplyRequest
          );
          parentComment.replies = parentComment.replies.filter(
            (r) => r.id !== id
          );
        }
      } else {
        const deleteCommentRequest: DeleteCommentRequest = {
          cellId: cellId,
          commentId: id,
        };
        await axios.post(
          import.meta.env.VITE_BACKEND_URL + "api/delete_comment",
          deleteCommentRequest
        );
        allComments.value = allComments.value.filter((c) => c.id !== id);
      }
    } catch (error) {
      console.error("Error deleting comment:", error);
    }
  }

  async function editComment(
    commentId: string,
    cellId: string,
    newCommentText: string,
    parentCommentId?: string
  ) {
    try {
      const editingComment = allComments.value.find(
        (c) => c.id === (parentCommentId ?? commentId)
      );
      if (parentCommentId) {
        const editReplyRequest: EditReplyRequest = {
          cellId: cellId,
          parentCommentId: parentCommentId,
          commentId: commentId,
          comment: newCommentText,
        };
        await axios.post(
          import.meta.env.VITE_BACKEND_URL + "api/edit_reply",
          editReplyRequest
        );
        const editingReply = editingComment?.replies.find(
          (r) => r.id === commentId
        );
        editingReply && (editingReply.comment = newCommentText);
      } else {
        const editCommentRequest: EditCommentRequest = {
          cellId: cellId,
          commentId: commentId,
          comment: newCommentText,
        };
        await axios.post(
          import.meta.env.VITE_BACKEND_URL + "api/edit_comment",
          editCommentRequest
        );
        editingComment && (editingComment.comment = newCommentText);
      }
    } catch (error) {
      console.error("Error editing comment:", error);
    }
  }

  async function replyComment(replyToCommentId: string, comment: Comment) {
    try {
      const addReplyRequest: AddReplyRequest = {
        cellId: comment.cell.cellId ?? "",
        parentCommentId: replyToCommentId,
        commentId: comment.id,
        comment: comment.comment,
        date: comment.date,
      };
      await axios.post(
        import.meta.env.VITE_BACKEND_URL + "api/add_reply",
        addReplyRequest
      );
      const commentReplyTo = allComments.value.find(
        (c) => c.id === replyToCommentId
      );
      commentReplyTo?.replies.push(comment);
    } catch (error) {
      console.error("Error replying to comment:", error);
    }
  }

  async function resolveComment(id: string, cellId: string) {
    try {
      const resolveCommentRequest: ResolveCommentRequest = {
        cellId: cellId,
        commentId: id,
        resolved: true,
      };
      await axios.post(
        import.meta.env.VITE_BACKEND_URL + "api/resolve_comment",
        resolveCommentRequest
      );
      const resolveComment = allComments.value.find((c) => c.id === id);
      if (resolveComment) resolveComment.resolved = true;
    } catch (error) {
      console.error("Error resolving comment:", error);
    }
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
    editorAvailable,
    // Getters,
    commentsByCell,
    displayedComments,
    // Actions
    addComment,
    editComment,
    deleteComment,
    replyComment,
    closeComments,
    resolveComment,
    showAllComments,
    showCommentsPerCell,
    loadComments,
  };
});
