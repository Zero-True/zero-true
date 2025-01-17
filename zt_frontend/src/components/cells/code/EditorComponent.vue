<template>
  <div>
    <codemirror
      v-model="localCode"
      :style="{ height: '400px' }"
      :autofocus="true"
      :indent-with-tab="true"
      :tab-size="2"
      :viewportMargin="Infinity"
      :extensions="extensions"
      :id="'codeMirror_' + cellId"
      @ready="handleReady"
      @keyup="handleKeyup"
      @focus="handleFocus"
      @blur="handleBlur"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, shallowRef, PropType, watch } from "vue";
import { Codemirror } from "vue-codemirror";
import { EditorView } from "@codemirror/view";

export default defineComponent({
  name: "EditorComponent",
  components: { codemirror: Codemirror },
  props: {
    code: {
      type: String,
      required: true,
    },
    extensions: {
      type: Array as PropType<any[]>,
      required: true,
    },
    cellId: {
      type: String,
      required: true,
    },
    isDevMode: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["update:code", "saveCell", "ready", "focus", "blur"],
  setup(props, { emit }) {
    const editorView = shallowRef<EditorView | null>(null);

    // Local state to manage the editor content
    const localCode = shallowRef(props.code);

    // Watch for external changes to `props.code` and update `localCode`
    watch(
      () => props.code,
      (newCode) => {
        if (newCode !== localCode.value) {
          localCode.value = newCode;
        }
      }
    );

    // Emit `update:code` whenever localCode changes
    const handleKeyup = () => {
      emit("update:code", localCode.value); // Sync localCode with the parent
      saveCell();
    };

    const saveCell = () => {
      if (editorView.value) {
        const position = editorView.value.state.selection.main.head;
        const line = editorView.value.state.doc.lineAt(position).number;
        const column = position - editorView.value.state.doc.line(line).from;
        emit("saveCell", { line, column, code: localCode.value });
      }
    };

    const handleReady = (payload: any) => {
      editorView.value = payload.view;
      emit("ready", payload);
    };

    const handleFocus = () => {
      emit("focus");
    };

    const handleBlur = () => {
      emit("blur");
    };

    return { localCode, handleKeyup, handleReady, handleFocus, handleBlur };
  },
});
</script>