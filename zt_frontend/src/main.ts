import App from "./App.vue";
import { createApp } from "vue";
import { createPinia } from 'pinia';
import "@mdi/font/css/materialdesignicons.css";
import "./styles/main.scss";
import { registerPlugins } from "@/plugins";

const pinia = createPinia();
const app = createApp(App);

app.use(pinia);

registerPlugins(app).then(() => {
    app.config.globalProperties.$devMode = "dev" === import.meta.env.VITE_APP_MODE;

    app.mount("#app");    
});
