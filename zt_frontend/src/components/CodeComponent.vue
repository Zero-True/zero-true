<template>
  <v-card flat color="bluegrey">
    <v-row v-if="$devMode" no-gutters class="py-1 toolbar-bg">
      <v-col :cols="11">
        <span class="py-0 px-2">.py</span>
        <!-- Placeholder for future content or can be empty -->
      </v-col>
      <v-col :cols="1" class="d-flex justify-end align-center py-0">
        <v-icon
          small
          class="mx-1"
          color="primary"
          @click="runCode(false, '', '')"
        >
          mdi-play
        </v-icon>
        <v-icon small class="mx-1" color="error" @click="deleteCell">
          mdi-delete
        </v-icon>
      </v-col>
    </v-row>
    <codemirror
      v-if="$devMode"
      v-model="cellData.code"
      :style="{ height: '400px' }"
      :autofocus="true"
      :indent-with-tab="true"
      :tab-size="2"
      :viewportMargin="Infinity"
      :extensions="extensions"
      @ready="handleReady"
      @keyup="saveCell"
    />
    <v-expansion-panels v-else>
      <v-expansion-panel>
        <v-expansion-panel-title color="bluegrey2">
          View Source Code
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
    <div v-if="$devMode">
      <p class="text-caption text-disabled text-right">
        CTRL+Enter to run</p>
    </div>
    <v-container>
      <layout-component
        v-for="(row, rowIndex) in cellData.layout?.rows"
        :key="rowIndex"
        :row-data="row"
        :components="cellData.components"
        @runCode="runCode"
      />
      <v-row>
        <v-col v-for="(col, colIndex) in columns" :cols="col.width">
          <layout-component
            :key="colIndex"
            :column-data="col"
            :components="cellData.components"
            @runCode="runCode"
          />
        </v-col>
      </v-row>
      <!-- Render unplaced components at the bottom -->
      <v-row>
        <v-container
          class="pa-1"
          v-for="component in unplacedComponents"
          :key="component.id"
        >
          <!-- Render Plotly component if it's a 'plotly-plot' -->
          <plotly-plot
            v-if="component.component === 'plotly-plot'"
            :id="component.id"
            :figure="component.figure"
            :layout="component.layout"
          />
          <!-- Render other components -->
          <component
            v-else-if="component.component === 'v-card'"
            :is="component.component"
            v-bind="componentBind(component)"
            position="relative"
            @runCode="runCode"
          >
            <div v-for="comp in cardComponents(component)">
              <plotly-plot
                v-if="comp.component === 'plotly-plot'"
                :id="component.id"
                :figure="comp.figure"
                :layout="comp.layout"
              />
              <component
                v-else
                :is="comp.component"
                v-bind="componentBind(comp)"
                v-model="comp.value"
                @click="clickedButton(comp)"
                @[comp.triggerEvent]="runCode(true, comp.id, comp.value)"
              />
            </div>
          </component>

          <component
            v-else
            :is="component.component"
            v-bind="componentBind(component)"
            v-model="component.value"
            @click="clickedButton(component)"
            @[component.triggerEvent]="
              runCode(true, component.id, component.value)
            "
          />
        </v-container>
      </v-row>
      <v-row>
        <v-col>
          <pre class="text-p">{{ cellData.output }}</pre>
        </v-col>
      </v-row>
    </v-container>
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
import type { PropType, ShallowRef } from "vue";
import { shallowRef } from "vue";
import PlotlyPlot from "@/components/PlotlyComponent.vue";
import { Codemirror } from 'vue-codemirror'
import { python } from '@codemirror/lang-python'
import { oneDark } from '@codemirror/theme-one-dark'
import { EditorView, keymap } from '@codemirror/view'
import { Prec } from "@codemirror/state";
import { autocompletion, CompletionResult, CompletionContext } from '@codemirror/autocomplete'
import {
  VSlider,
  VTextField,
  VTextarea,
  VRangeSlider,
  VSelect,
  VCombobox,
  VBtn,
  VImg,
  VAutocomplete,
  VCard,
} from "vuetify/lib/components/index.mjs";
import { VDataTable } from "vuetify/labs/VDataTable";
import { CodeCell, Layout } from "@/types/notebook";
import { Completion } from "@/types/completions";
import LayoutComponent from "@/components/LayoutComponent.vue";
import TextComponent from "@/components/TextComponent.vue"

export default {
  components: {
    "codemirror": Codemirror,
    "v-slider": VSlider,
    "v-text-field": VTextField,
    "v-number-field": VTextField,
    "v-textarea": VTextarea,
    "v-range-slider": VRangeSlider,
    "v-select": VSelect,
    "v-combobox": VCombobox,
    "v-btn": VBtn,
    "v-img": VImg,
    "v-data-table": VDataTable,
    "v-autocomplete": VAutocomplete,
    "v-card": VCard,
    "v-text": TextComponent,
    "plotly-plot": PlotlyPlot,
    "layout-component": LayoutComponent,
  },
  props: {
    cellData: {
      type: Object as PropType<CodeCell>,
      required: true,
    },
    completions: {
      type: Object as PropType<Completion>,
      required: true
    }
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

  setup() {    
    const view: ShallowRef<EditorView|null>=shallowRef(null);
    const handleReady = (payload:any) => {view.value = payload.view};

    return { view, handleReady };
  },


  computed: {
    extensions(){
      const handleCtrlEnter = () => {
        this.runCode(false,'','')
      }
      const keyMap = keymap.of([
      { 
          key: "Ctrl-Enter", 
          run: () => {
            handleCtrlEnter();
            return true;
          }
        }
      ]);
      const customCompletionSource = async (context: CompletionContext) => {
        console.log('here')
        const word = context.matchBefore(/\w*/);
        const from = word ? word.from : context.pos;

        return {
              from: from,
              options: this.completions.map((completion: { label: any; type: any; }) => ({
                label: completion.label,
                type: completion.type,
                apply: (view: { dispatch: (arg0: { changes: { from: any; to: any; insert: any } }) => void }, completion: { label: any }, from: any, to: any) => {
                  const insertText = completion.label;
                  view.dispatch({
                    changes: { from: from, to: to ?? context.pos, insert: insertText }
                  });
                }
              }))
            };
          };
      return [Prec.highest(keyMap), python(), oneDark, autocompletion({ override: [customCompletionSource] })]
    },

    columns() {
      return this.cellData.layout?.columns || [];
    },

    unplacedComponents() {
      const findPlacedIds = (items: any[]): string[] => {
        let ids: string[] = [];
        for (const item of items) {
          for (const component of item?.components ?? []) {
            if (typeof component === "string") {
              // It's an ID of a regular component
              ids.push(component);
            } else if (component && component.components) {
              // It's a nested row, go deeper
              ids = ids.concat(findPlacedIds([component]));
            }
          }
        }
        return ids;
      };

      const findCardIds = (items: any[]): string[] => {
        let ids: string[] = [];
        for (const comp of items) {
          if (comp.component === "v-card") {
            ids.push.apply(ids, Object.values(comp.cardChildren));
          }
        }
        return ids;
      };

      const placedComponentIds = findPlacedIds(
        (this.cellData.layout as Layout)?.rows ?? []
      )
        .concat(findPlacedIds((this.cellData.layout as Layout)?.columns ?? []))
        .concat(findCardIds(this.cellData.components));
      return this.cellData.components.filter(
        (comp) => !placedComponentIds.includes(comp.id)
      );
    },
  },

  methods: {
    runCode(fromComponent: boolean, componentId: string, componentValue: any) {
      if (!this.$devMode && fromComponent) {
        this.$emit(
          "componentChange",
          this.cellData.id,
          componentId,
          componentValue
        );
      } else {
        this.$emit("runCode", this.cellData.id, componentId);
      }
    },
    deleteCell() {
      this.$emit("deleteCell", this.cellData.id);
    },
    componentBind(component: any) {
      if (component.component && component.component === "v-autocomplete") {
        const { value, ...rest } = component;
        return this.convertUnderscoresToHyphens(rest);
      }
      return this.convertUnderscoresToHyphens(component);
    },

    convertUnderscoresToHyphens(obj: any) {
      return Object.entries(obj).reduce((newObj: any, [key, value]) => {
        const modifiedKey = key.replace(/_/g, '-');
        newObj[modifiedKey] = value;
        return newObj;
      }, {});
    },
    clickedButton(component: any) {
      if (component.component === "v-btn") {
        component.value = true;
      }
    },
    findComponentById(id: string) {
      const component = this.cellData.components.find((comp) => comp.id === id);
      return component;
    },
    cardComponents(card: any) {
      const cardComponents: any[] = [];
      for (const id in card.cardChildren) {
        cardComponents.push(this.findComponentById(card.cardChildren[id]));
      }
      return cardComponents;
    },
    createCell(cellType: string){
      this.$emit("createCell", this.cellData.id, cellType);
    },
    saveCell() {
      if (!this.view?.hasFocus) return
      const position = this.view?.state.selection.main.head;
      const line = this.view?.state.doc.lineAt(position).number;
      const column = position - this.view?.state.doc.line(line).from;
      this.$emit("saveCell", this.cellData.id, this.cellData.code, line, column);
    },
  },
};
</script>

<style>
.toolbar-bg {
  background-color: #4f4d4d; /* Light grey background */
}
</style>
