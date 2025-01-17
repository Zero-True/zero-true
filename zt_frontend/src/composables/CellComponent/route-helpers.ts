import { computed } from "vue";
import { useRoute } from "vue-router";

export function useRouteHelpers() {
  const isAppRoute = computed(() => useRoute().name === "/app");
  return { isAppRoute };
}
