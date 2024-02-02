<template>
  <cell
    cell-type="sql"
    :cell-id="cellData.id" 
    :is-dev-mode="$devMode && !isAppRoute && !isMobile"
    @play="runCode" 
    @delete="deleteCell"
    @addCell="e => createCell(e)"
  >
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
      />
      <v-expansion-panels v-else>
          <v-expansion-panel  
            bg-color="#212121"
          >
          <v-expansion-panel-title 
            color="#1c2e3c"
          >
            View Source Code
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <v-text-field
              v-model="cellData.variable_name"
              label="Enter SQL variable name"
              density="compact"
              :readonly="true"
            />
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
      <div v-if="$devMode && !isAppRoute && !isMobile">
        <p class="text-caption text-disabled text-right">CTRL+Enter to run</p>
      </div>
    </template>
    <template v-slot:outcome>
      <v-container
        v-if="$devMode && !isAppRoute && !isMobile"
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
import { VDataTable } from "vuetify/labs/VDataTable";
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
      ]);
      if (this.$devMode) {
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
  emits: ['runCode', 'deleteCell', 'createCell', 'saveCell'],
  data() {
    return {
      isFocused: false, // add this line to keep track of the focus state
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
      this.$emit("runCode", this.cellData.id);
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
  },
};
</script>
