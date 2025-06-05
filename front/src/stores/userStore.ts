import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

// 定义用户接口
export interface User {
  id: number
  username: string
  email: string
  token?: string
  is_admin?: boolean
}

export const useUserStore = defineStore('user', () => {
  // 用户数据
  const currentUser = ref<User | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  // API基础URL
  const apiBaseUrl = 'http://localhost:5000/api'
  
  // 配置axios拦截器
  axios.interceptors.request.use(
    (config) => {
      const token = currentUser.value?.token
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )
  
  // 计算属性：是否已登录
  const isLoggedIn = computed(() => !!currentUser.value)
  
  // 计算属性：是否是管理员
  const isAdmin = computed(() => !!currentUser.value?.is_admin)
  
  // 初始化：从localStorage加载用户信息
  function initUser() {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      try {
        currentUser.value = JSON.parse(savedUser)
      } catch (e) {
        localStorage.removeItem('user')
        currentUser.value = null
      }
    }
  }
  
  // 登录
  async function login(username: string, password: string) {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await axios.post(`${apiBaseUrl}/login`, { username, password })
      const { user, token } = response.data
      
      // 保存用户信息，包括管理员状态
      currentUser.value = {
        id: user.id,
        username: user.username,
        email: user.email,
        is_admin: user.is_admin,
        token: token
      }
      
      // 保存到localStorage
      localStorage.setItem('user', JSON.stringify(currentUser.value))
      return true
    } catch (e: any) {
      error.value = e.response?.data?.message || '登录失败，请检查用户名和密码'
      return false
    } finally {
      isLoading.value = false
    }
  }
  
  // 注册
  async function register(username: string, email: string, password: string) {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await axios.post(`${apiBaseUrl}/register`, { 
        username, 
        email, 
        password 
      })
      
      return true
    } catch (e: any) {
      error.value = e.response?.data?.message || '注册失败，请稍后再试'
      return false
    } finally {
      isLoading.value = false
    }
  }
  
  // 登出
  function logout() {
    currentUser.value = null
    localStorage.removeItem('user')
  }
  
  return {
    currentUser,
    isLoading,
    error,
    isLoggedIn,
    isAdmin,
    initUser,
    login,
    register,
    logout
  }
})