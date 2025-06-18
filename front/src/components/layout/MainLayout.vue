<template>
  <div class="layout-container">
    <header class="header">
      <div class="logo">Game Store</div>
      <div class="nav-center">
        <nav class="main-nav">
          <button @click="navigateToCart" class="nav-item">购物车</button>
          <router-link to="/store" class="nav-item">商店</router-link>
          <button @click="navigateToLibrary" class="nav-item">游戏库</button>
          <router-link v-if="userStore.isAdmin" to="/admin" class="nav-item admin">管理</router-link>
        </nav>
      </div>
      <div class="user-actions">
        <template v-if="userStore.isLoggedIn">
          <div class="user-dropdown">
            <button class="btn-user-menu">
              {{ userStore.currentUser?.username }}
              <span v-if="userStore.isAdmin" class="admin-badge">管理员</span>
              ▼
            </button>
            <div class="dropdown-menu">
              <router-link v-if="userStore.isAdmin" to="/admin" class="dropdown-item">管理页面</router-link>
              <button @click="handleLogout" class="dropdown-item">登出</button>
            </div>
          </div>
        </template>
        <template v-else>
          <button @click="showLoginModal" class="btn-login">登录</button>
          <button @click="showRegisterModal" class="btn-register">注册</button>
        </template>
      </div>
    </header>
    
    <main class="main-content">
      <router-view />
    </main>
    
    <footer class="footer">
      <p>&copy; 2025 Game Store - 游戏数据库实验</p>
    </footer>
    
    <!-- 认证模态框 -->
    <AuthModal 
      v-if="showAuthModal" 
      :initial-form="authModalType" 
      @close="showAuthModal = false"
      @login-success="handleLoginSuccess"
      @register-success="handleRegisterSuccess"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/userStore'
import { useGameStore } from '@/stores/gameStore'
import { useRouter } from 'vue-router'
import AuthModal from '../auth/AuthModal.vue'

export default defineComponent({
  name: 'MainLayout',
  components: {
    AuthModal
  },
  setup() {
    const userStore = useUserStore()
    const gameStore = useGameStore()
    const router = useRouter()
    const showAuthModal = ref(false)
    const authModalType = ref('login')
    
    // 初始化用户信息
    onMounted(() => {
      userStore.initUser()
    })
    
    const navigateToCart = () => {
      if (!userStore.isLoggedIn) {
        alert('请先登录')
        return
      }
      router.push('/cart')
    }
    
    const navigateToLibrary = () => {
      if (!userStore.isLoggedIn) {
        alert('请先登录')
        return
      }
      router.push('/library')
    }
    
    const showLoginModal = () => {
      authModalType.value = 'login'
      showAuthModal.value = true
    }
    
    const showRegisterModal = () => {
      authModalType.value = 'register'
      showAuthModal.value = true
    }
    
    const handleLoginSuccess = () => {
      // 登录成功后加载用户数据
      gameStore.loadUserCart()
      gameStore.loadUserLibrary()
      // 强制跳转到主页面
      router.push('/store')
    }
    
    const handleRegisterSuccess = () => {
      // 注册成功的处理
      // 强制跳转到主页面
      router.push('/store')
    }
    
    const handleLogout = () => {
      userStore.logout()
      // 强制跳转到主页面
      router.push('/store')
    }
    
    return {
      userStore,
      showAuthModal,
      authModalType,
      navigateToCart,
      navigateToLibrary,
      showLoginModal,
      showRegisterModal,
      handleLoginSuccess,
      handleRegisterSuccess,
      handleLogout
    }
  }
})
</script>

<style scoped>
.layout-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #171a21;
  color: white;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
}

.nav-center {
  flex-grow: 1;
  display: flex;
  justify-content: center;
}

.main-nav {
  display: flex;
  gap: 2rem;
}

.nav-item {
  color: #c7d5e0;
  text-decoration: none;
  font-size: 1.4rem;
  padding: 0.5rem 1rem;
  border-radius: 10px;
  transition: background-color 0.3s;
  background: #082538;
  border: none;
  cursor: pointer;
  font-weight: bold;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.admin {
  background-color: #b12020;
  color: white;
}

.nav-item.admin:hover {
  background-color: #d42626;
}

.user-actions {
  display: flex;
  gap: 1rem;
}

.btn-login, .btn-register {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.2rem;
}

.btn-login {
  background-color: transparent;
  color: #c7d5e0;
  border: 1px solid #c7d5e0;
}

.btn-register {
  background-color: #5c7e10;
  color: white;
}

.main-content {
  flex-grow: 1;
  padding: 2rem;
  background-color: #1b2838;
  color: #c7d5e0;
}

.footer {
  padding: 1rem 2rem;
  background-color: #171a21;
  color: #8f98a0;
  text-align: center;
}

/* 用户下拉菜单样式 */
.user-dropdown {
  position: relative;
}

.btn-user-menu {
  background-color: #387198;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.3rem;
  font-weight: bold;
}

.admin-badge {
  background-color: #db2323c8;
  color: white;
  font-size: 1.1rem;
  padding: 0.2rem 0.3rem;
  border-radius: 4px;
  margin-left: 0.5rem;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: #2a475e;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  min-width: 150px;
  z-index: 10;
  display: none;
}

.user-dropdown:hover .dropdown-menu {
  display: block;
}

.dropdown-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: 0.8rem 1rem;
  border: none;
  background: none;
  color: #c7d5e0;
  cursor: pointer;
  font-size: 0.9rem;
  text-decoration: none;
}

.dropdown-item:hover {
  background-color: #387198;
  color: white;
}
</style>