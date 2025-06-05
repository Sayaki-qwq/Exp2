import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'

import App from './App.vue'
import router from './router'
import { useUserStore } from './stores/userStore'

// 设置axios默认值
axios.defaults.baseURL = 'http://localhost:5000'
axios.defaults.withCredentials = true

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

// 初始化用户状态
const userStore = useUserStore(pinia)
userStore.initUser()

app.mount('#app')
