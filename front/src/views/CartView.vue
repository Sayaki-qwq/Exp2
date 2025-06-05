<template>
  <div class="cart-container">
    <h1>购物车</h1>
    
    <div v-if="gameStore.cartItems.length === 0" class="empty-cart">
      <p>您的购物车是空的</p>
      <router-link to="/store" class="btn-continue-shopping">继续购物</router-link>
    </div>
    
    <div v-else class="cart-content">
      <div class="cart-items">
        <div v-for="item in gameStore.cartItems" :key="item.game.id" class="cart-item">
          <div class="cart-item-image">
            <img :src="item.game.imageUrl" :alt="item.game.title">
          </div>
          <div class="cart-item-info">
            <h3 class="cart-item-title">{{ item.game.title }}</h3>
            <p class="cart-item-developer">开发商: {{ item.game.developer }}</p>
          </div>
          <div class="cart-item-price">
            ¥{{ item.game.price }}
          </div>
          <div class="cart-item-actions">
            <button @click="gameStore.removeFromCart(item.game.id)" class="btn-remove">
              移除
            </button>
          </div>
        </div>
      </div>
      
      <div class="cart-summary">
        <div class="cart-total">
          <h3>订单摘要</h3>
          <div class="total-row">
            <span>商品数量:</span>
            <span>{{ gameStore.cartCount }}</span>
          </div>
          <div class="total-row">
            <span>总价:</span>
            <span class="price">¥{{ gameStore.cartTotal }}</span>
          </div>
          <button @click="checkout" class="btn-checkout">结算</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted } from 'vue'
import { useGameStore } from '@/stores/gameStore'
import { useUserStore } from '@/stores/userStore'
import { useRouter } from 'vue-router'

export default defineComponent({
  name: 'CartView',
  setup() {
    const gameStore = useGameStore()
    const userStore = useUserStore()
    const router = useRouter()
    
    // 在组件挂载时加载购物车数据
    onMounted(async () => {
      if (!userStore.isLoggedIn) {
        router.push('/login')
        return
      }
      await gameStore.loadUserCart()
    })
    
    const checkout = async () => {
      try {
        const success = await gameStore.purchaseGames()
        if (success) {
          router.push('/library')
      }
      } catch (error) {
        console.error('结算失败', error)
      }
    }
    
    return {
      gameStore,
      checkout
    }
  }
})
</script>

<style scoped>
.cart-container {
  padding: 1rem;
}

.empty-cart {
  text-align: center;
  margin-top: 3rem;
}

.btn-continue-shopping {
  display: inline-block;
  background-color: #5c7e10;
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  margin-top: 1rem;
  transition: background-color 0.3s;
}

.btn-continue-shopping:hover {
  background-color: #6d9619;
}

.cart-content {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 2rem;
  margin-top: 2rem;
}

.cart-items {
  background-color: #2a475e;
  border-radius: 8px;
  padding: 1rem;
}

.cart-item {
  display: grid;
  grid-template-columns: 100px 1fr auto auto;
  gap: 1rem;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #1b2838;
}

.cart-item:last-child {
  border-bottom: none;
}

.cart-item-image img {
  width: 100%;
  height: 50px;
  object-fit: cover;
  border-radius: 4px;
}

.cart-item-title {
  margin: 0;
  font-size: 1rem;
}

.cart-item-developer {
  margin: 0.5rem 0 0 0;
  font-size: 0.8rem;
  color: #8f98a0;
}

.cart-item-quantity,
.btn-quantity,
.quantity {
  display: none;
}

.cart-item-price {
  font-weight: bold;
  color: #c7d5e0;
}

.btn-remove {
  background-color: #c23b22;
  color: white;
  border: none;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.cart-summary {
  background-color: #2a475e;
  border-radius: 8px;
  padding: 1rem;
  align-self: start;
}

.cart-total h3 {
  margin-top: 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #1b2838;
}

.total-row {
  display: flex;
  justify-content: space-between;
  margin: 1rem 0;
}

.price {
  font-weight: bold;
  font-size: 1.2rem;
}

.btn-checkout {
  background-color: #5c7e10;
  color: white;
  border: none;
  padding: 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  width: 100%;
  margin-top: 1rem;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.btn-checkout:hover {
  background-color: #6d9619;
}
</style>