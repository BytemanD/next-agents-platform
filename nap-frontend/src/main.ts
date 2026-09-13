import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

import '@fontsource-variable/space-grotesk'

import '@unocss/reset/tailwind.css'
import 'uno.css'
import 'tdesign-vue-next/es/style/index.css'
import 'tdesign-vue-next/es/grid/style/index.css'
import './styles/theme1.css'

import TDesignChat from '@tdesign-vue-next/chat'


const app = createApp(App)
app.use(TDesignChat)

app.use(createPinia())
app.use(router)

app.mount('#app')
