<template>
  <cell
    cell-type="text"
    :cell-id="cellData.id"
    :is-dev-mode="$devMode && !isAppRoute && !isMobile"
    :hide-cell="(cellData.hideCell as boolean)"
    :cell-name="(cellData.cellName as string)"
    :cell-has-output="true"
    :is-focused="isFocused"
    @save="saveCell"
    @delete="deleteCell"
    @addCell="(e) => createCell(e)"  >
    <template v-slot:code>
      <tiny-editor
        v-if="$devMode && !isAppRoute && !isMobile"
        v-model="cellData.code"
        :init="editorConfig"
        @keyUp="saveCell"
        @focus="onEditorFocus"
        @blur="onEditorBlur"
      />
    </template>
    <template v-slot:outcome v-if="($devMode && isAppRoute) || !$devMode">
      <tiny-editor v-model="cellData.code" :init="app_init" :disabled="true" />
    </template>
  </cell>
</template>

<script lang="ts">
import type { PropType } from "vue";
import "tinymce/tinymce";
import "tinymce/models/dom";
import "tinymce/themes/silver";
import "tinymce/icons/default";
import "tinymce/skins/ui/tinymce-5-dark/skin.css";
import "tinymce/plugins/autoresize";
import "tinymce/plugins/advlist";
import "tinymce/plugins/autolink";
import "tinymce/plugins/lists";
import "tinymce/plugins/link";
import "tinymce/plugins/table";
import "tinymce/plugins/image";
import Editor from "@tinymce/tinymce-vue";
import { CodeCell } from "@/types/notebook";
import { useRoute } from "vue-router";
import Cell from "@/components/Cell.vue";

export default {
  components: {
    cell: Cell,
    "tiny-editor": Editor,
  },
  props: {
    cellData: {
      type: Object as PropType<CodeCell>,
      required: true,
    },
  },
  inheritAttrs: false,
  emits: ["saveCell", "deleteCell", "createCell", 'navigateToCell'],
  data() {
    return {
      init: {
        plugins: "autoresize advlist autolink lists link image table",
        toolbar:
          "undo redo | bold italic underline strikethrough | fontfamily fontsize blocks | alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist | forecolor backcolor removeformat | pagebreak | charmap emoticons | fullscreen  preview save print | insertfile image media template link anchor codesample table | ltr rtl",
        branding: false,
        menubar: false,
        statusbar: false,
        skin: false,
        content_css: false,
        font_formats:
          "Roboto=Roboto, sans-serif;Arial=arial,helvetica,sans-serif;Courier New=courier new,courier,monospace;",
        content_style:
          "body { background-color: #FFFFFF; color: #1B2F3C; font-family: 'Roboto', sans-serif; }",
        autoresize_bottom_margin: 10,
        min_height: 100,
        license_key: "gpl",
      },
      app_init: {
        plugins: "autoresize",
        toolbar: false,
        branding: false,
        menubar: false,
        statusbar: false,
        skin: false,
        content_css: false,
        font_formats:
          "Roboto=Roboto, sans-serif;Arial=arial,helvetica,sans-serif;Courier New=courier new,courier,monospace;",
        content_style:
          "body { background-color: #FFFFFF; color: #1B2F3C; font-family: 'Roboto', sans-serif; }",
        min_height: 0,
        autoresize_bottom_margin: 0,
        license_key: "gpl",
      },
      items: [
        { title: "Code" },
        { title: "SQL" },
        { title: "Markdown" },
        { title: "Text" },
      ],
      editor: null,
      isFocused: false,
    };
  },
  computed: {
    isAppRoute() {
      const route = useRoute();
      return route.path === "/app";
    },
    isMobile() {
      return this.$vuetify.display.mobile;
    },
    editorConfig() {
      return {
        ...this.init,
        setup: (editor: any) => {
          // Store editor reference on setup
          this.editor = editor;
          editor.on('init', () => {
            this.handleEditorInit(editor);
          });

          editor.on('keydown', (e: any) => {
            if (e.keyCode === 38) { // Up arrow
              const isAtStart = this.isCursorAtStart(editor);
              if (isAtStart) {
                e.preventDefault();
                this.$emit('navigateToCell', this.cellData.id, 'up');
              }
            }

            if (e.keyCode === 40) { // Down arrow
              const isAtEnd = this.isCursorAtEnd(editor);
              if (isAtEnd) {
                e.preventDefault();
                this.$emit('navigateToCell', this.cellData.id, 'down');
              }
            }
          });
        }
      };
    }
  },
  methods: {
    saveCell() {
      if (!this.$devMode) return;
      this.$emit("saveCell", this.cellData.id, this.cellData.code, "", "");
    },
    deleteCell() {
      this.$emit("deleteCell", this.cellData.id);
    },
    createCell(cellType: string) {
      this.$emit("createCell", this.cellData.id, cellType);
    },
    getEditorView() {
        return this.editor;
    },

    isCursorAtStart(editor: any): boolean {
    const selection = editor.selection;
    const rng = selection.getRng(true);
    const body = editor.getBody();

    if (!body || !body.childNodes.length) return true;

    const blocks = Array.from(body.childNodes as NodeListOf<ChildNode>).flatMap((node: Node) => {
        if (node.nodeName === "UL" || node.nodeName === "OL") {
            return Array.from(node.childNodes).filter((child: Node) => child.nodeName === "LI");
        }
        return ["P", "DIV", "LI", "H1", "H2", "H3", "H4", "H5", "H6"].includes((node as HTMLElement).nodeName)
            ? [node]
            : [];
    });

    if (!blocks.length) return true;

    const firstBlock = blocks[0] as HTMLElement;
    const currentBlock = editor.dom.getParent(rng.startContainer, "p,div,li,h1,h2,h3,h4,h5,h6,ul,ol");

    if (currentBlock !== firstBlock) return false;

    // Handle links at start
    if (rng.startContainer.nodeType === Node.ELEMENT_NODE && 
        (rng.startContainer as HTMLElement).nodeName === "A") {
        return rng.startOffset === 0;
    }

    const isFirstBlockEmpty = !firstBlock.textContent?.trim() || firstBlock.innerHTML === "<br>";
    const isAtTextStart = rng.startContainer.nodeType === Node.TEXT_NODE && rng.startOffset === 0;

    return isFirstBlockEmpty || isAtTextStart;
},
// Modify isCursorAtEnd method
isCursorAtEnd(editor: any): boolean {
    const selection = editor.selection;
    const rng = selection.getRng(true);
    const body = editor.getBody();

    if (!body.childNodes.length) return true;

    const blocks = Array.from(body.childNodes as NodeListOf<ChildNode>).flatMap((node: Node) => {
        if (node.nodeName === "UL" || node.nodeName === "OL") {
            return Array.from(node.childNodes).filter((child: Node) => child.nodeName === "LI");
        }
        return ["P", "DIV", "LI", "H1", "H2", "H3", "H4", "H5", "H6"].includes((node as HTMLElement).nodeName)
            ? [node]
            : [];
    });

    if (!blocks.length) return true;

    const lastBlock = blocks[blocks.length - 1] as HTMLElement;
    const currentBlock = editor.dom.getParent(rng.endContainer, "p,div,li,h1,h2,h3,h4,h5,h6,ul,ol");

    if (currentBlock !== lastBlock) return false;

    const isLastBlockEmpty = !lastBlock.textContent?.trim() || 
                           lastBlock.innerHTML === "<br>" || 
                           lastBlock.childNodes.length === 0;

    if (isLastBlockEmpty) return true;

    // Handle links at end
    if (rng.endContainer.nodeType === Node.ELEMENT_NODE && 
        (rng.endContainer as HTMLElement).nodeName === "A") {
        const link = rng.endContainer as HTMLElement;
        return rng.endOffset === link.childNodes.length;
    }

    // Handle lists
    if (lastBlock.nodeName === "LI") {
        const listItem = lastBlock as HTMLLIElement;
        return rng.endOffset === (listItem.textContent || "").length;
    }

    const isAtTextEnd = rng.endContainer.nodeType === Node.TEXT_NODE &&
                       rng.endOffset === (rng.endContainer.textContent || "").length;

    return isAtTextEnd && !rng.endContainer.nextSibling;
},

  handleEditorInit(editor: any) {
    this.editor = editor;

    editor.on("keydown", (e: any) => {
      try {
        if (e.keyCode === 38) {
          const isAtStart = this.isCursorAtStart(editor);
          console.log("Up arrow pressed. Is at start:", isAtStart);
          if (isAtStart) {
            e.preventDefault();
            this.$emit("navigateToCell", this.cellData.id, "up");
          }
        }

        if (e.keyCode === 40) {
          const isAtEnd = this.isCursorAtEnd(editor);
          console.log("Down arrow pressed. Is at end:", isAtEnd);
          if (isAtEnd) {
            e.preventDefault();
            this.$emit("navigateToCell", this.cellData.id, "down");
          }
        }
      } catch (error) {
        console.error("Error in editor navigation:", error);
      }
    });
  },
  handleFocus(focus: boolean) {
      console.log('EditorComponent handleFocus:', focus);
      this.isFocused = focus;
    },
    onEditorFocus() {
      this.handleFocus(true);
    },
    onEditorBlur() {
      this.handleFocus(false);
    }
    },
};
</script>

<style>
.tox .tox-toolbar,
.tox .tox-toolbar__primary,
.tox .tox-toolbar__overflow {
  background-color: #FFFFFF !important;
}
.tox-tinymce {
  border: none !important;
}
</style>