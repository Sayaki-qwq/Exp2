import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'

import App from './App.vue'
import router from './router'

// 检查是否是页面刷新
const isPageRefresh = window.performance && window.performance.navigation.type === 1

// 如果不是页面刷新（即是新的会话），则清除localStorage
if (!isPageRefresh) {
  localStorage.removeItem('user')
  delete axios.defaults.headers.common['Authorization']
}

// 设置axios默认值
axios.defaults.baseURL = 'http://localhost:5000'
axios.defaults.withCredentials = true

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
