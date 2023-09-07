import App from './App.vue'
import { createApp } from 'vue'

import { registerPlugins } from '@/plugins'

const app = createApp(App)
registerPlugins(app)

app.config.globalProperties.$appMode = 'app' === import.meta.env.VITE_APP_MODE;

app.mount('#app')
