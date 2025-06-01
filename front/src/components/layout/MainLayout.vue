<template>
  <div class="main-layout">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-container">
        <!-- Logo -->
        <div class="logo">
          <h1>GameStore</h1>
        </div>
        
        <!-- 右上角登录注册按钮 -->
        <div class="auth-buttons">
          <button 
            class="btn btn-outline" 
            @click="showLogin"
            v-if="!isLoggedIn"
          >
            登录
          </button>
          <button 
            class="btn btn-primary" 
            @click="showRegister"
            v-if="!isLoggedIn"
          >
            注册
          </button>
          <div class="user-menu" v-if="isLoggedIn">
            <span class="username">{{ username }}</span>
            <button class="btn btn-outline" @click="logout">退出</button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content">
      <!-- 中间导航选项 -->
      <nav class="main-nav">
        <div class="nav-container">
          <button 
            class="nav-item"
            :class="{ active: activeTab === 'store' }"
            @click="setActiveTab('store')"
          >
            <div class="nav-icon">🏪</div>
            <span>商店</span>
          </button>
          <button 
            class="nav-item"
            :class="{ active: activeTab === 'cart' }"
            @click="setActiveTab('cart')"
          >
            <div class="nav-icon">🛒</div>
            <span>购物车</span>
            <span class="cart-badge" v-if="cartCount > 0">{{ cartCount }}</span>
          </button>
        </div>
      </nav>

      <!-- 内容展示区域 -->
      <div class="content-area">
        <div v-if="activeTab === 'store'" class="tab-content">
          <GameStore 
            @add-to-cart="handleAddToCart" 
            @add-to-wishlist="handleAddToWishlist" 
          />
        </div>
        <div v-if="activeTab === 'cart'" class="tab-content">
          <Cart 
            :cart-items="cartItems"
            @remove-from-cart="handleRemoveFromCart"
            @move-to-wishlist="handleMoveToWishlist"
            @clear-cart="handleClearCart"
            @purchase-games="handlePurchaseGames"
            @update-cart-count="handleUpdateCartCount"
          />
        </div>
      </div>
    </main>

    <!-- 登录弹窗 -->
    <div class="modal-overlay" v-if="showLoginModal" @click="closeModals">
      <div class="modal" @click.stop>
        <h3>登录</h3>
        <form @submit.prevent="handleLogin">
          <input 
            type="text" 
            v-model="loginForm.username" 
            placeholder="用户名"
            class="input-field"
          >
          <input 
            type="password" 
            v-model="loginForm.password" 
            placeholder="密码"
            class="input-field"
          >
          <div class="modal-buttons">
            <button type="button" class="btn btn-outline" @click="closeModals">取消</button>
            <button type="submit" class="btn btn-primary">登录</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 注册弹窗 -->
    <div class="modal-overlay" v-if="showRegisterModal" @click="closeModals">
      <div class="modal" @click.stop>
        <h3>注册</h3>
        <form @submit.prevent="handleRegister">
          <input 
            type="text" 
            v-model="registerForm.username" 
            placeholder="用户名"
            class="input-field"
          >
          <input 
            type="email" 
            v-model="registerForm.email" 
            placeholder="邮箱"
            class="input-field"
          >
          <input 
            type="password" 
            v-model="registerForm.password" 
            placeholder="密码"
            class="input-field"
          >
          <input 
            type="password" 
            v-model="registerForm.confirmPassword" 
            placeholder="确认密码"
            class="input-field"
          >
          <div class="modal-buttons">
            <button type="button" class="btn btn-outline" @click="closeModals">取消</button>
            <button type="submit" class="btn btn-primary">注册</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import GameStore from '../store/GameStore.vue'
import Cart from '../cart/GameCart.vue'

// 游戏接口定义
interface Game {
  id: number
  title: string
  description: string
  releaseDate: string
  price: number
  developer: string
  publisher: string
  coverImage: string
  inCart: boolean
  inWishlist: boolean
}

// 响应式数据
const activeTab = ref<'store' | 'cart'>('store')
const isLoggedIn = ref(false)
const username = ref('')
const cartCount = ref(0)
const showLoginModal = ref(false)
const showRegisterModal = ref(false)

// 购物车数据
const cartItems = ref<Game[]>([])
const wishlistItems = ref<Game[]>([])

// 表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// 方法
const setActiveTab = (tab: 'store' | 'cart') => {
  activeTab.value = tab
}

const showLogin = () => {
  showLoginModal.value = true
}

const showRegister = () => {
  showRegisterModal.value = true
}

const closeModals = () => {
  showLoginModal.value = false
  showRegisterModal.value = false
  // 清空表单
  Object.assign(loginForm, { username: '', password: '' })
  Object.assign(registerForm, { username: '', email: '', password: '', confirmPassword: '' })
}

const handleLogin = () => {
  // TODO: 实际的登录逻辑
  console.log('登录:', loginForm)
  // 模拟登录成功
  isLoggedIn.value = true
  username.value = loginForm.username
  closeModals()
}

const handleRegister = () => {
  // TODO: 实际的注册逻辑
  if (registerForm.password !== registerForm.confirmPassword) {
    alert('密码不一致')
    return
  }
  console.log('注册:', registerForm)
  // 模拟注册成功
  isLoggedIn.value = true
  username.value = registerForm.username
  closeModals()
}

const logout = () => {
  isLoggedIn.value = false
  username.value = ''
  activeTab.value = 'store'
  // 清空购物车和愿望单
  cartItems.value = []
  wishlistItems.value = []
  cartCount.value = 0
}

// 购物车相关事件处理
const handleAddToCart = (game: Game) => {
  // 检查游戏是否已在购物车中
  const existingItem = cartItems.value.find(item => item.id === game.id)
  if (!existingItem) {
    const gameToAdd = { ...game, inCart: true }
    cartItems.value.push(gameToAdd)
    cartCount.value = cartItems.value.length
    console.log('添加到购物车:', game.title)
  }
}

const handleRemoveFromCart = (game: Game) => {
  const index = cartItems.value.findIndex(item => item.id === game.id)
  if (index > -1) {
    cartItems.value.splice(index, 1)
    cartCount.value = cartItems.value.length
    // 更新游戏的购物车状态
    game.inCart = false
    console.log('从购物车移除:', game.title)
  }
}

const handleMoveToWishlist = (game: Game) => {
  // 从购物车移除
  handleRemoveFromCart(game)
  
  // 添加到愿望单（如果不存在）
  const existingWishItem = wishlistItems.value.find(item => item.id === game.id)
  if (!existingWishItem) {
    const gameToAdd = { ...game, inWishlist: true, inCart: false }
    wishlistItems.value.push(gameToAdd)
    console.log('移至愿望单:', game.title)
  }
}

const handleClearCart = () => {
  // 将所有购物车中的游戏状态重置
  cartItems.value.forEach(game => {
    game.inCart = false
  })
  cartItems.value = []
  cartCount.value = 0
  console.log('购物车已清空')
}

const handlePurchaseGames = (games: Game[]) => {
  console.log('购买成功:', games.map(g => g.title))
  // 清空购物车
  handleClearCart()
  // 可以在这里添加购买后的逻辑，比如添加到游戏库等
}

const handleUpdateCartCount = (count: number) => {
  cartCount.value = count
}

const handleAddToWishlist = (game: Game) => {
  if (game.inWishlist) {
    // 从愿望单移除
    const index = wishlistItems.value.findIndex(item => item.id === game.id)
    if (index > -1) {
      wishlistItems.value.splice(index, 1)
      game.inWishlist = false
      console.log('从愿望单移除:', game.title)
    }
  } else {
    // 添加到愿望单
    const existingItem = wishlistItems.value.find(item => item.id === game.id)
    if (!existingItem) {
      const gameToAdd = { ...game, inWishlist: true }
      wishlistItems.value.push(gameToAdd)
      game.inWishlist = true
      console.log('添加到愿望单:', game.title)
    }
  }
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  color: white;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.header-container {
  width: 100%;
  padding: 1rem 3rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-sizing: border-box;
}

.logo h1 {
  margin: 0;
  font-size: 2.5rem;
  font-weight: bold;
  background: linear-gradient(45deg, #ffffff, #a8edea);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.auth-buttons {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.username {
  font-weight: 500;
  color: #a8edea;
}

.main-content {
  width: 100%;
  min-height: calc(100vh - 80px);
  padding: 3rem;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.main-nav {
  margin-bottom: 3rem;
  width: 100%;
}

.nav-container {
  display: flex;
  justify-content: center;
  gap: 3rem;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 2rem 3rem;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid transparent;
  border-radius: 20px;
  color: white;
  font-size: 2rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  min-width: 150px;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.2);
  border-color: #a8edea;
  box-shadow: 0 0 20px rgba(168, 237, 234, 0.3);
}

.nav-icon {
  font-size: 3rem;
}

.cart-badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: #ff4757;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: bold;
}

.content-area {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 3rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  flex: 1;
  width: 100%;
  box-sizing: border-box;
  min-height: 500px;
}

.tab-content {
  height: 100%;
}

.tab-content h2 {
  margin-top: 0;
  color: #a8edea;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1.6rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(45deg, #a8edea, #fed6e3);
  color: #2c3e50;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(168, 237, 234, 0.4);
}

.btn-outline {
  background: transparent;
  border: 2px solid rgba(255, 255, 255, 0.5);
  color: white;
}

.btn-outline:hover {
  border-color: white;
  background: rgba(255, 255, 255, 0.1);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 15px;
  width: 100%;
  max-width: 400px;
  color: #2c3e50;
}

.modal h3 {
  margin-top: 0;
  text-align: center;
  color: #2c3e50;
}

.input-field {
  width: 100%;
  padding: 1rem;
  margin-bottom: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1.5rem;
  box-sizing: border-box;
}

.input-field:focus {
  outline: none;
  border-color: #a8edea;
}

.modal-buttons {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-container {
    padding: 1rem 1.5rem;
  }
  
  .main-content {
    padding: 1.5rem;
  }
  
  .nav-container {
    gap: 1rem;
  }
  
  .nav-item {
    padding: 1.5rem 2rem;
    min-width: 120px;
    font-size: 1.6rem;
  }
  
  .nav-icon {
    font-size: 2.5rem;
  }
  
  .content-area {
    padding: 1.5rem;
  }
  
  .logo h1 {
    font-size: 2rem;
  }
  
  .auth-buttons {
    gap: 0.5rem;
  }
  
  .btn {
    font-size: 1.4rem;
    padding: 0.6rem 1.2rem;
  }
}
</style>