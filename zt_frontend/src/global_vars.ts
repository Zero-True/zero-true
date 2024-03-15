import { reactive } from 'vue';
import { Timer } from "@/timer";

declare module "@vue/runtime-core" {
  interface ComponentCustomProperties {
    $devMode: boolean;
  }
}

export {};

export const globalState = reactive({
    copilot_active: false,
    timers: {} as {[key: string]: {[key: string]: Timer}},
});