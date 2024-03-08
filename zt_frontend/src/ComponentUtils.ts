import { ZTComponent } from "@/types/notebook";

// Mixin for shared component utilities
export const sharedComponentUtils = {
  methods: {
    clickedButton(component: any) {
      if (component.component === "v-btn" || component.component === "v-timer") {
        component.value = true;
      }
    },
  },
};
