/**
 * plugins/index.ts
 *
 * Automatically included in `./src/main.ts`
 */

// Plugins
import { loadFonts } from "./webfontloader";
import vuetify from "./vuetify";
import { createRouter, createWebHistory } from 'vue-router/auto'
import axios from 'axios'
// Types
import type { App } from "vue";

export async function registerPlugins(app: App) {
  const response = await axios.get(import.meta.env.VITE_BACKEND_URL + "base_path");
  const baseUrl = response.data;

  // Create the router with the fetched base URL
  const router = createRouter({
    history: createWebHistory(baseUrl),
    // ... (other router options like routes)
  });
  loadFonts();
  app 
  .use(vuetify)
  .use(router);
}
