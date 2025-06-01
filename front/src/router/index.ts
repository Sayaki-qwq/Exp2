// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/components/layout/MainLayout.vue'

const routes = [
  {
    path: '/',
    component: MainLayout
  }
]

export default createRouter({
  history: createWebHistory(),
  routes
})