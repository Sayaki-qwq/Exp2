// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/components/layout/MainLayout.vue'
import StoreView from '@/views/StoreView.vue'
import CartView from '@/views/CartView.vue'
import LibraryView from '@/views/LibraryView.vue'
import GameDetailView from '@/views/GameDetailView.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        redirect: '/store'
      },
      {
        path: 'store',
        component: StoreView
      },
      {
        path: 'game/:id',
        component: GameDetailView
      },
      {
        path: 'cart',
        component: CartView
      },
      {
        path: 'library',
        component: LibraryView
      }
    ]
  }
]

export default createRouter({
  history: createWebHistory(),
  routes
})