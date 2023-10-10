<template>
    <v-row v-if="rowData">
        <v-col v-for="(component, componentIndex) in rowData.components" :key="componentIndex" :cols="componentWidth(component)">
            <div v-if="typeof component==='string'">
                <div v-for="comp in findComponentById(component)">
                    <!-- Logic to conditionally render Plotly component -->
                    <plotly-plot 
                        
                        v-if="comp.component === 'plotly-plot'"
                        :figure="comp.figure"
                        :layout="comp.layout"
                    />
                    <!-- Logic to render other types of components -->
                    <component
                        v-else
                        :is="comp.component"
                        v-bind="componentBind(comp)"
                        v-model="comp.value"
                        @click="clickedButton(comp)"
                        @[comp.triggerEvent]="runCode(comp.id, comp.value)"
                    />
                </div>
            </div>
            <div v-else>
                <layout-component 
                    :column-data="component"
                    :components="components"
                    @runCode="runCode"/>
            </div>
        </v-col>
    </v-row>
    <div v-if="columnData">
        <div v-for="(component, componentIndex) in columnData.components" :key="componentIndex">
            <div v-if="typeof component==='string'">
                <div v-for="comp in findComponentById(component)">
                    <!-- Logic to conditionally render Plotly component -->
                    <plotly-plot 
                        
                        v-if="comp.component === 'plotly-plot'"
                        :figure="comp.figure"
                        :layout="comp.layout"
                    />

                    <!-- Logic to render other types of components -->
                    <component
                        v-else
                        :is="comp.component"
                        v-bind="componentBind(comp)"
                        v-model="comp.value"
                        @click="clickedButton(comp)"
                        @[comp.triggerEvent]="runCode(comp.id, comp.value)"
                    />
                </div>
            </div>
            <div v-else>
                <layout-component 
                    :row-data="component"
                    :components="components"
                    @runCode="runCode"/>
            </div>
        </div>
    </div>
    
</template>

<script lang="ts">
import type { PropType } from 'vue'
import { VSlider, VTextField, VTextarea, VRangeSlider, VSelect, VCombobox, VBtn, VImg, VAutocomplete } from 'vuetify/lib/components/index.mjs';
import { VDataTable } from "vuetify/labs/VDataTable";
import { Column, ZTComponent, Row } from '@/types/notebook';
import PlotlyPlot from '@/components/PlotlyComponent.vue';

export default {
    components: {
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
      'plotly-plot': PlotlyPlot,
    },
    props: {
        rowData: {
            type: Object as PropType<Row>
        },
        columnData: {
            type: Object as PropType<Column>
        },
        components: {
            type: Object as PropType<ZTComponent[]>,
            required: true
        }
    },
    methods: {
        findComponentById(id: string) {
            const component = this.components.find(comp => comp.id === id);
            return component ? [component] : [];
        },
        runCode(componentId: string, componentValue: any) {
            this.$emit('runCode', true, componentId, componentValue);
        },
        componentWidth(component: any){
            return component.width ? component.width : false
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
        }
    }
}

</script>