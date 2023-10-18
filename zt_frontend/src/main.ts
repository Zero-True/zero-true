import App from './App.vue'
import { createApp } from 'vue'
import '@mdi/font/css/materialdesignicons.css';
import { registerPlugins } from '@/plugins'

const app = createApp(App)
registerPlugins(app)

app.config.globalProperties.$devMode = 'dev' === import.meta.env.VITE_APP_MODE;

app.mount('#app')
