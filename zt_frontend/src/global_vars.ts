import { reactive } from 'vue';

declare module "@vue/runtime-core" {
  interface ComponentCustomProperties {
    $devMode: boolean;
  }
}

export {};

export const globalState = reactive({
    copilot_active: false
});