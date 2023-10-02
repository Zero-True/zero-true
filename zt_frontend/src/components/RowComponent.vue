<template>
    <v-row>
        <v-col v-for="(col, colIndex) in rowData.columns" :key="colIndex">
            <div v-for="(component, componentIndex) in col.components" :key="componentIndex">
                <div v-if="typeof component==='string'">
                    <component v-for="comp in findComponentById(component)"
                        :is="comp.component"
                        v-bind="comp"
                        v-model="comp.value"
                        @[comp.triggerEvent]="runCode"
                    />
                </div>
                <div v-else>
                    <row-component 
                        :row-data="component"
                        :components="components"/>
                </div>
            </div>
        </v-col>
    </v-row>
</template>

<script lang="ts">
import type { PropType } from 'vue'
import { VSlider, VTextField, VTextarea, VRangeSlider, VSelect, VCombobox, VBtn, VImg } from 'vuetify/lib/components/index.mjs';
import { VDataTable } from "vuetify/labs/VDataTable";
import { ZTComponent, ZTRow } from '@/types/notebook';

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
    },
    props: {
        rowData: {
            type: Object as PropType<ZTRow>,
            required: true,
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
        runCode() {
            this.$emit('runCode');
        },
    }
}

</script>