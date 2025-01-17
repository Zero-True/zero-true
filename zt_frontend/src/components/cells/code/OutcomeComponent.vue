<template>
  <div>
    <!-- Main output container -->
    <div :id="'outputContainer_' + cellId">
      <!-- Render layout rows -->
      <layout-component
        v-if="layout?.rows?.length"
        v-for="(row, rowIndex) in layout.rows"
        :key="rowIndex"
        :row-data="row"
        :components="compDict"
        @runCode="runCode"
      />
      
      <!-- Render unplaced components -->
      <div v-if="unplacedComponents.length" :id="'unplacedComponents_' + cellId">
        <component-wrapper
          :renderComponents="unplacedComponents"
          :allComponents="compDict"
          @runCode="runCode"
        />
      </div>

      <!-- Render output -->
      <pre class="code-output" :id="'cellOutput_' + cellId">{{ output }}</pre>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue";
import LayoutComponent from "@/components/cells/base/LayoutComponent.vue";
import ComponentWrapper from "@/components/cells/base/ComponentWrapper.vue";
import { Layout, ZTComponent } from "@/types/notebook";

export default defineComponent({
  name: "OutcomeComponent",
  components: {
    "layout-component": LayoutComponent,
    "component-wrapper": ComponentWrapper,
  },
  props: {
    cellId: {
      type: String,
      required: true,
    },
    layout: {
      type: Object as PropType<Layout>,
      required: false,
    },
    unplacedComponents: {
      type: Array as PropType<ZTComponent[]>,
      required: true,
    },
    output: {
      type: String,
      required: false,
      default: "",
    },
    compDict: {
      type: Object as PropType<Record<string, ZTComponent>>,
      required: true,
    },
  },
  emits: ["runCode"],
  methods: {
    runCode(componentId: string, componentValue: any) {
      this.$emit("runCode", componentId, componentValue);
    },
  },
});
</script>
