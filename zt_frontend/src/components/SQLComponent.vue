<template>
  <v-card flat color="bluegrey">
    <v-row v-if="$devMode && !isAppRoute" no-gutters class="py-1 toolbar-bg">
      <v-col :cols="11">
        <span class="py-0 px-2">.sql</span>

        <!-- Placeholder for future content or can be empty -->
      </v-col>
      <v-col :cols="1" class="d-flex justify-end align-center py-0">
        <v-icon small class="mx-1" color="primary" @click="runCode">
          mdi-play
        </v-icon>
        <v-icon small class="mx-1" color="error" @click="deleteCell">
          mdi-delete
        </v-icon>
      </v-col>
    </v-row>
    <v-text-field
      v-if="$devMode && !isAppRoute"
      v-model="cellData.variable_name"
      label="Enter SQL variable name"
      density="compact"
    />
    <codemirror
      v-if="$devMode && !isAppRoute"
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
      <v-expansion-panel>
        <v-expansion-panel-title color="bluegrey2">
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
    <div v-if="$devMode && !isAppRoute">
      <p class="text-caption text-disabled text-right">CTRL+Enter to run</p>
    </div>
    <v-container
      v-if="$devMode && !isAppRoute"
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
  </v-card>
  <v-menu v-if="$devMode && !isAppRoute" transition="scale-transition">
    <template v-slot:activator="{ props }">
      <v-btn v-bind="props" color="#212121" block>
        <v-row>
          <v-icon color="primary">mdi-plus</v-icon>
        </v-row>
      </v-btn>
    </template>

    <v-list>
      <v-list-item v-for="(item, i) in items" :key="i">
        <v-btn block @click="createCell(item.title)">{{ item.title }}</v-btn>
      </v-list-item>
    </v-list>
  </v-menu>
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

export default {
  components: {
    codemirror: Codemirror,
    "v-data-table": VDataTable,
  },

  computed: {
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

  data() {
    return {
      isFocused: false, // add this line to keep track of the focus state
      isAppRoute: false,
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
    this.checkRoute();
  },
  methods: {
    checkRoute() {
      const route = useRoute();
      if (route.path === "/app") {
        this.isAppRoute = true;
      }
    },
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
