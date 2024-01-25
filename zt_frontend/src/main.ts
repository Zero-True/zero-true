import App from "./App.vue";
import { createApp } from "vue";
import "@mdi/font/css/materialdesignicons.css";
import "./styles/main.scss";
import { registerPlugins } from "@/plugins";

const app = createApp(App);
registerPlugins(app).then(() => {
    app.config.globalProperties.$devMode = "dev" === import.meta.env.VITE_APP_MODE;

    app.mount("#app");    
});
