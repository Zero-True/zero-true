<template>
  <v-card class="card">
    <div
      class="d-flex justify-space-between align-center pa-4"
      v-if="selectedCell"
    >
      <div class="d-flex align-center">
        <v-icon
          :icon="`ztIcon:${ztAliases[cellTypeIcon ?? 'code']}`"
          :color="cellTypeColor"
          class="mr-2"
        ></v-icon>
        <p class="mb-0 font-weight-bold" :style="{ color: cellTypeColor }">
          {{ selectedCell.cellName }}
        </p>
      </div>
      <div class="justify-right">
        <v-btn
          v-if="!resolvedMode"
          icon="mdi-comment-plus-outline"
          color="bluegrey-darken-4"
          :disabled="!commentsStore.editorAvailable"
          @click="addCommentClick"
        >
        </v-btn>

        <v-btn
          icon="mdi:mdi-close"
          variant="text"
          :ripple="false"
          @click="closeComments()"
        ></v-btn>
      </div>
    </div>

    <div class="content ma-4">
      <div class="d-flex justify-space-between align-center">
        <v-btn-toggle
          v-model="resolvedMode"
          :border="false"
          mandatory="force"
          color="primary"
          rounded="pill"
        >
          <v-btn :value="false" class="mr-4">Open</v-btn>
          <v-btn :value="true" class="mr-4">Resolved</v-btn>
        </v-btn-toggle>
      </div>
      <div class="mt-6 flex-1-1">
        <div
          class="empty-state"
          v-if="
            !commentsStore.displayedComments.length &&
            !displayAddCommentTextarea
          "
        >
          <v-icon :icon="`ztIcon:${ztAliases.message}`" />
          <p>No comments yet</p>
          <p class="empty-state__text mt-2">
            Add a comment by clicking on the cell you want to add a comment to.
          </p>
        </div>
        <div class="comments-wrapper" v-else>
          <Comment v-for="comment in displayedComments" :comment="comment" />
          <div
            class="text-box"
            v-if="displayAddCommentTextarea"
            ref="addCommentContainer"
          >
            <v-textarea
              variant="outlined"
              v-model="newCommentText"
              ref="addCommentTextArea"
            ></v-textarea>
            <div class="d-flex justify-end">
              <v-btn
                variant="text"
                @click="
                  () => {
                    commentsStore.editorAvailable = true;
                    displayAddCommentTextarea = false;
                  }
                "
                >Cancel</v-btn
              >
              <v-btn
                color="primary"
                class="ml-2"
                :disabled="!newCommentText || savingNewComment"
                :loading="savingNewComment"
                @click="submitNewComment()"
                >Submit</v-btn
              >
            </div>
          </div>
        </div>
      </div>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { ztAliases } from "@/iconsets/ztIcon";
import Comment from "./Comment.vue";
import { useCommentsStore } from "@/stores/comments";
import { v4 as uuidv4 } from "uuid";

const commentsStore = useCommentsStore();

const { addComment, closeComments } = commentsStore;
const { selectedCell } = storeToRefs(commentsStore);

const addCommentTextArea = ref<HTMLElement | null>(null);
const addCommentContainer = ref<HTMLElement | null>(null);

const cellTypeIcon = computed(() => {
  return selectedCell.value?.cellType;
});

const cellTypeColor = computed(() => {
  switch (selectedCell.value?.cellType) {
    case "markdown":
      return "#4CBCFC";
    case "code":
      return "#AE9FE8";
    case "sql":
      return "#FFDCA7";
    case "text":
      return "#16B48E";
  }
});

const resolvedMode = shallowRef(false);
const displayAddCommentTextarea = shallowRef(false);
const newCommentText = shallowRef("");
const savingNewComment = shallowRef(false);

const displayedComments = computed(() =>
  commentsStore.displayedComments.filter((c) => {
    if (resolvedMode.value) {
      return c.resolved;
    } else {
      return !c.resolved;
    }
  })
);

watch(selectedCell, () => {
  // Reset component variables
  resolvedMode.value = false;
  displayAddCommentTextarea.value = false;
  newCommentText.value = "";
  savingNewComment.value = false;
});

function addCommentClick() {
  displayAddCommentTextarea.value = !displayAddCommentTextarea.value;
  commentsStore.editorAvailable = false;
  nextTick(() => {
    addCommentTextArea.value?.scrollIntoView({
      behavior: "smooth",
      block: "nearest",
      inline: "start",
    });
    addCommentTextArea.value?.focus();
  });
}

async function submitNewComment() {
  savingNewComment.value = true;
  const options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  };
  const date = Intl.DateTimeFormat("en-US", options).format(new Date());
  const newComment = {
    id: uuidv4(),
    cell: commentsStore.selectedCell!,
    userName: "",
    date: date,
    comment: newCommentText.value,
    replies: [],
    resolved: false,
  };

  await addComment(newComment);
  savingNewComment.value = false;
  newCommentText.value = "";
  displayAddCommentTextarea.value = false;
  commentsStore.editorAvailable = true;
}
</script>

<style lang="scss" scoped>
.card {
  position: sticky;
  height: 87.5vh;
  top: 3.9rem;
}
.close-btn {
  position: absolute;
  top: 0;
  right: 0;
}
.content {
  position: relative;
  height: 100%;
}
.empty-state {
  margin-top: 200px;
  text-align: center;
  &__text {
    max-width: 20em;
    margin: 0 auto;
    line-height: 1.8rem;
    color: rgb(var(--v-theme-bluegrey));
  }
}
.comments-wrapper {
  max-height: 66vh;
  overflow-y: auto;
}
</style>
