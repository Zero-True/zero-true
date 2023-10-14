<template>
  <v-card flat color="bluegrey">
    <ace-editor
        v-if="$devMode"
        v-model:value="cellData.code"
        ref="editor"
        class="editor"
        theme="dracula"
        lang="python"
        :options="editorOptions"
      />
    <v-expansion-panels v-else>
      <v-expansion-panel>
        <v-expansion-panel-title color="bluegrey2">
          View Source Code
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <ace-editor
            v-model:value="cellData.code"
            ref="editor"
            class="editor"
            theme="dracula"
            lang="python"
            :readonly=true
            :options="editorOptions"
          />
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>

    <v-toolbar v-if="$devMode" color="bluegrey">
      <v-btn variant="flat" color="primary" @click="runCode(false, '', '')">Run</v-btn>
      <v-spacer />
      <v-btn variant="flat" color="error" @click="deleteCell">Delete Cell</v-btn>
    </v-toolbar>
    <v-container>    
      <layout-component v-for="(row, rowIndex) in cellData.layout?.rows"
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
        <v-container class="pa-1" v-for="component in unplacedComponents" :key="component.id" >
          <!-- Render Plotly component if it's a 'plotly-plot' -->
          <plotly-plot
            v-if="component.component === 'plotly-plot'"
            :id="component.id"
            :figure="component.figure"
            :layout="component.layout"
          />
          <!-- Render other components -->
          <component 
            v-else-if="component.component==='v-card'" 
            :is="component.component" 
            v-bind="componentBind(component)" 
            position="relative"
            @runCode="runCode">
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
                @[comp.triggerEvent]="runCode(true, comp.id, comp.value)"/>
            </div>
          </component>

          <component
            v-else
            :is="component.component"
            v-bind="componentBind(component)"
            v-model="component.value"
            @click="clickedButton(component)"
            @[component.triggerEvent]="runCode(true, component.id, component.value)"/>
        </v-container>
      </v-row>  
      <v-row>
        <v-col>
          <div class="text-p">{{cellData.output}}</div>
        </v-col>
      </v-row>
    </v-container>
  </v-card>
</template>

  
  <script lang="ts">
  import type { PropType } from 'vue'
  import PlotlyPlot from '@/components/PlotlyComponent.vue';
  import { VAceEditor } from 'vue3-ace-editor';
  import 'ace-builds/src-noconflict/mode-python';
  import 'ace-builds/src-noconflict/snippets/python';
  import 'ace-builds/src-noconflict/ext-language_tools';
  import 'ace-builds/src-noconflict/theme-dracula';
  import { VSlider, VTextField, VTextarea, VRangeSlider, VSelect, VCombobox, VBtn, VImg, VAutocomplete, VCard } from 'vuetify/lib/components/index.mjs';
  import { VDataTable } from "vuetify/labs/VDataTable";
  import { CodeCell, Layout } from '@/types/notebook';
  import LayoutComponent from '@/components/LayoutComponent.vue';
  
  export default {
    components: {
      'ace-editor': VAceEditor,
      'v-slider': VSlider,
      'v-text-field': VTextField,
      'v-number-field': VTextField,
      'v-textarea': VTextarea,
      'v-range-slider': VRangeSlider,
      'v-select': VSelect,
      'v-combobox': VCombobox,
      'v-btn': VBtn,
      'v-img': VImg,
      'v-data-table': VDataTable,
      'v-autocomplete': VAutocomplete,
      'v-card': VCard,
      'plotly-plot': PlotlyPlot,
      'layout-component': LayoutComponent,
    },
    props: {
      cellData: {
        type: Object as PropType<CodeCell>,
        required: true,
      },
    },
  
    
    computed: {

      columns(){
        return this.cellData.layout?.columns || []
      },

      editorOptions() {
        return {
          showPrintMargin: false,
          enableBasicAutocompletion: true,
          enableSnippets: true,
          enableLiveAutocompletion: true,
          autoScrollEditorIntoView: true,
          highlightActiveLine: this.$devMode,
          highlightGutterLine: this.$devMode,
          minLines: 5,
          maxLines: Infinity,
        };
      },
      unplacedComponents() {
        const findPlacedIds = (items: any[]): string[] => {
          let ids: string[] = [];
          for (const item of items) {
            for (const component of item?.components ?? []) {
                if (typeof component === 'string') {
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
          for (const comp of items){
            if(comp.component==='v-card'){
              ids.push.apply(ids, Object.values(comp.cardChildren))
            }
          }
          return ids
        }

        const placedComponentIds = findPlacedIds((this.cellData.layout as Layout)?.rows ?? []).concat(findPlacedIds((this.cellData.layout as Layout)?.columns ?? [])).concat(findCardIds(this.cellData.components));
        return this.cellData.components.filter(
          comp => !placedComponentIds.includes(comp.id)
        );
      }
    },
    methods: {
      runCode(fromComponent:boolean , componentId: string, componentValue: any) {
        if (!this.$devMode && fromComponent){
          this.$emit('componentChange', this.cellData.id, componentId, componentValue);
        }
        else{
          this.$emit('runCode', this.cellData.id, componentId);
        }
      },
      deleteCell() {
        this.$emit('deleteCell', this.cellData.id);
      },
      componentBind(component: any){
        if(component.component && component.component === 'v-autocomplete'){
          const { value, ...rest } = component;
          return rest
        }
        return component
      },
      clickedButton(component: any){
          if(component.component==='v-btn'){
              component.value=true
          }
      },
      findComponentById(id: string) {
          const component = this.cellData.components.find(comp => comp.id === id);
          return component;
      },
      cardComponents(card: any) {
        const cardComponents: any[] = []
        for(const id in card.cardChildren){
          cardComponents.push(this.findComponentById(card.cardChildren[id]))
        }
        return cardComponents
      }
    },
  }
  </script>