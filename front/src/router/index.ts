// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/components/layout/MainLayout.vue'
import StoreView from '@/views/StoreView.vue'
import CartView from '@/views/CartView.vue'
import LibraryView from '@/views/LibraryView.vue'
import GameDetailView from '@/views/GameDetailView.vue'
import AdminView from '@/views/AdminView.vue'
import { useUserStore } from '@/stores/userStore'

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
      },
      {
        path: 'admin',
        component: AdminView,
        meta: { requiresAdmin: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 检查是否需要管理员权限
  if (to.matched.some(record => record.meta.requiresAdmin)) {
    // 如果用户未登录或不是管理员，重定向到首页
    if (!userStore.isLoggedIn || !userStore.isAdmin) {
      next({ path: '/' })
      return
    }
  }
  
  next()
})

export default router