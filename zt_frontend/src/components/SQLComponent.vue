<template>
  <v-card flat color="bluegrey">
    <v-row v-if="$devMode" no-gutters class="py-1 toolbar-bg">
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
      v-if="$devMode"
      v-model="cellData.variable_name"
      label="Enter SQL variable name"
      density="compact"
    />
    <codemirror
      v-if="$devMode"
      v-model="cellData.code"
      :style="{ height: '400px' }"
      :autofocus="true"
      :indent-with-tab="true"
      :tab-size="2"
      :viewportMargin="Infinity"
      :extensions="extensions"
      @focus="handleFocus(true)"
      @blur="handleFocus(false)"
    />
    <v-expansion-panels v-else>
      <v-expansion-panel>
        <v-expansion-panel-title color="bluegrey2">
          View Source Code
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <codemirror
            v-if="$devMode"
            v-model="cellData.code"
            :style="{ height: '400px' }"
            :autofocus="true"
            :indent-with-tab="true"
            :tab-size="2"
            :viewportMargin="Infinity"
            :extensions="extensions"
            @focus="handleFocus(true)"
            @blur="handleFocus(false)"
          />
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
    <div v-if="$devMode">
      <p class="text-caption text-disabled text-right">
        CTRL+Enter to run</p>
    </div>
    <v-container v-for="component in cellData.components" :key="component.id">
      <component
        :is="component.component"
        v-bind="component"
        v-model="component.value"
        @[component.triggerEvent]="runCode"
      />
    </v-container>
    <div class="text-p">{{ cellData.output }}</div>
  </v-card>
  <v-menu transition="scale-transition">
    <template v-slot:activator="{ props }">
      <v-btn v-bind="props" block>
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
import type { PropType } from "vue";
import { VDataTable } from "vuetify/labs/VDataTable";
import { Codemirror } from 'vue-codemirror'
import { sql } from '@codemirror/lang-sql'
import { oneDark } from '@codemirror/theme-one-dark'
import { EditorView } from '@codemirror/view'
import { autocompletion, CompletionResult, CompletionContext } from '@codemirror/autocomplete'
import { CodeCell } from "@/types/notebook";

export default {
  components: {
    "codemirror": Codemirror,
    "v-data-table": VDataTable,
  },

  computed: {
    extensions() {return [sql(), oneDark, autocompletion({ override: [] })]},
  },
  
  data() {
    return {
      isFocused: false, // add this line to keep track of the focus state
      items: [
        { title: 'Code' },
        { title: 'SQL' },
        { title: 'Markdown' },
        { title: 'Text' },
      ],
    };
  },
  props: {
    cellData: {
      type: Object as PropType<CodeCell>,
      required: true,
    },
  },
  mounted() {
    // Attach the event listener when the component is mounted
    window.addEventListener("keydown", this.handleKeyDown);
  },
  beforeUnmount() {
    // Remove the event listener before the component is destroyed
    window.removeEventListener("keydown", this.handleKeyDown);
  },

  methods: {
    handleKeyDown(event: KeyboardEvent) {
      if (this.isFocused && event.ctrlKey && event.key === "Enter") {
        this.runCode();
      }
    },
    handleFocus(state: boolean) {
      this.isFocused = state;
    },
    runCode() {
      this.$emit("runCode", this.cellData.id);
    },
    deleteCell() {
      this.$emit("deleteCell", this.cellData.id);
    },
    createCell(cellType: string){
      this.$emit("createCell", this.cellData.id, cellType);
    }
  },
};
</script>
