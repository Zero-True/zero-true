<template>
  <cell
    cell-type="sql"
    :cell-id="cellData.id" 
    :hide-cell="(cellData.hideCell as boolean)"
    :hide-code="(cellData.hideCode as boolean)"
    :expand-code="(cellData.expandCode as boolean)"
    :non-reactive="(cellData.nonReactive as boolean)"
    :showTable="(cellData.showTable as boolean)"
    :cell-name="(cellData.cellName as string)"
    :cell-has-output="hasCellContent"
    :currentlyExecutingCell="currentlyExecutingCell"
    :isCodeRunning="isCodeRunning"
    :is-dev-mode="$devMode && !isAppRoute && !isMobile"
    :is-focused="isFocused"
    @play="runCode" 
    @delete="deleteCell"
    @expandCodeUpdate="e => expandCodeUpdate(e)"
    @hideCode="e => hideCode(e)"
    @updateReactivity="e => updateReactivity(e)"
    @updateShowTable="e => updateShowTable(e)"
    @renameCell="e => renameCell(e)"
    @addCell="e => createCell(e)"
  >
    <template v-slot:header-title>
      <div v-if="!$devMode || isAppRoute || isMobile" style="display: flex; width: 100%;">
        <h4 v-if="cellData.hideCode" class="text-bluegrey-darken-1 text-ellipsis app-static-name" >{{ cellData.cellName }} </h4>
        <v-expansion-panels v-else v-model="expanded">
          <v-expansion-panel  v-model="expanded" bg-color="bluegrey-darken-3">
            <v-expansion-panel-title class="text-bluegrey-darken-1">
              <h4 class="text-ellipsis app-static-name" > {{ cellData.cellName }} </h4>
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <codemirror
                v-model="cellData.code"
                :style="{ height: '400px' }"
                :autofocus="true"
                :indent-with-tab="true"
                :tab-size="2"
                :viewportMargin="Infinity"
                :extensions="extensions"
              />
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </div>
    </template>

    <template v-slot:code>
      <v-text-field
        v-if="$devMode && !isAppRoute && !isMobile"
        v-model="cellData.variable_name"
        label="Enter SQL variable name"
        density="compact"
      />
      <codemirror
        v-if="$devMode && !isAppRoute && !isMobile"
        v-model="cellData.code"
        :style="{ height: '400px' }"
        :autofocus="true"
        :indent-with-tab="true"
        :tab-size="2"
        :viewportMargin="Infinity"
        :extensions="extensions"
        @keyup="saveCell"
        @ready="handleReady"
        @focus="onEditorFocus"
        @blur="onEditorBlur"
      />
    </template>
    <template v-slot:outcome>
      <v-container
        v-if="($devMode && !isAppRoute) || cellData.showTable"
        v-for="component in cellData.components"
        :key="component.id"
      >
        <component
          :is="component.component"
          v-bind="component"
          v-model="component.value"
          @[component.triggerEvent]="runCode"
        />
      </v-container>
      <div class="text-p">{{ cellData.output }}</div>
    </template>
  </cell>
</template>

<script lang="ts">
import type { PropType, ShallowRef } from "vue";
import { shallowRef } from "vue";
import { VDataTable } from "vuetify/components/VDataTable";
import { Codemirror } from "vue-codemirror";
import { sql } from "@codemirror/lang-sql";
import { oneDark } from "@codemirror/theme-one-dark";
import { EditorView, keymap } from "@codemirror/view";
import { Prec, EditorState } from "@codemirror/state";
import {
  autocompletion,
  CompletionResult,
  CompletionContext,
} from "@codemirror/autocomplete";
import { CodeCell } from "@/types/notebook";
import { useRoute } from "vue-router";
import Cell from '@/components/Cell.vue'

export default {
  components: {
    "cell": Cell,
    codemirror: Codemirror,
    "v-data-table": VDataTable,
  },

  computed: {
    isAppRoute() {
      const route = useRoute()
      return route.path === '/app'
    },
    isMobile() {
      return this.$vuetify.display.mobile
    },
    hasCellContent() {
    const hasOutput = Boolean(this.cellData.output?.trim());
    const hasComponents = Boolean(this.cellData.components?.length > 0);
    return hasOutput || hasComponents;
  },
    extensions() {
      const handleCtrlEnter = () => {
        this.runCode();
      };
      const keyMap = keymap.of([
        {
          key: "Ctrl-Enter",
          run: () => {
            if (this.$devMode) {
              handleCtrlEnter();
            }
            return true;
          },
        },
        {
      key: 'ArrowUp',
      run: (view) => {
        if (view.state.selection.main.from === 0) {
          this.$emit('navigateToCell', this.cellData.id, 'up');
          return true;
        }
        return false;
      },
    },
      ]);
      if (this.$devMode && !this.isAppRoute) {
        return [
          Prec.highest(keyMap),
          sql(),
          oneDark,
          autocompletion({ override: [] }),
        ];
      }
      return [
        EditorState.readOnly.of(true),
        Prec.highest(keyMap),
        sql(),
        oneDark,
        autocompletion({ override: [] }),
      ];
    },
  },
  inheritAttrs: false,
  emits: ['runCode', 'deleteCell', 'createCell', 'saveCell','navigateToCell'],
  data() {
    return {
      isFocused: false, // add this line to keep track of the focus state
      expanded: this.cellData.expandCode ? [0] : [],
      items: [
        { title: "Code" },
        { title: "SQL" },
        { title: "Markdown" },
        { title: "Text" },
      ],
    };
  },
  props: {
    cellData: {
      type: Object as PropType<CodeCell>,
      required: true,
    },
      currentlyExecutingCell: {
      type: String,
      default: null
    },
    isCodeRunning:{
      type: Boolean,
      default: false
    },
  },
  setup() {
    const view: ShallowRef<EditorView | null> = shallowRef(null);
    const handleReady = (payload: any) => {
      view.value = payload.view;
    };

    return { view, handleReady };
  },
  mounted() {
  },
  methods: {
    runCode() {
      this.$emit("runCode", this.cellData.id, this.cellData.nonReactive);
    },
    deleteCell() {
      this.$emit("deleteCell", this.cellData.id);
    },
    createCell(cellType: string) {
      this.$emit("createCell", this.cellData.id, cellType);
    },
    saveCell() {
      if (!this.$devMode) return;
      this.$emit("saveCell", this.cellData.id, this.cellData.code, "", "");
    },
    expandCodeUpdate(e: Boolean){
      this.expanded = e ? [0] : []
    },
    updateReactivity(e: Boolean){
      this.cellData.nonReactive = e as boolean
    },
    updateShowTable(e: Boolean){
      this.cellData.showTable = e as boolean
    },
    hideCode(e: Boolean){
      this.cellData.hideCode = e as boolean
    },
    renameCell(e: String){
      this.cellData.cellName = e as string
    },
    getEditorView() {
      return this.view || null;
    },
    onEditorFocus() {
    this.isFocused = true;
  },
  onEditorBlur() {
    this.isFocused = false;
  },
  },
};
</script>
<style lang="scss" scoped>
.app-static-name {
  cursor: text; 
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>