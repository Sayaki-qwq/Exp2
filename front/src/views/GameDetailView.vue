<template>
  <div class="game-detail-container" v-if="game">
    <div class="game-detail-header">
      <div class="game-image-large">
        <img :src="game.imageUrl" :alt="game.title">
      </div>
      <div class="game-header-info">
        <h1 class="game-title">{{ game.title }}</h1>
        <div class="game-meta">
          <p class="game-developer">开发商: {{ game.developer }}</p>
          <p class="game-publisher">发行商: {{ game.publisher }}</p>
          <p class="game-release">发行日期: {{ game.releaseDate }}</p>
          <p class="game-type">类型: {{ game.type }}</p>
        </div>
      </div>
    </div>
    
    <div class="game-detail-content">
      <div class="game-description-section">
        <h2>游戏简介</h2>
        <p class="game-description-full">{{ game.description }}</p>
      </div>
      
      <div class="game-purchase-section">
        <div class="game-price-card">
          <h3>购买 {{ game.title }}</h3>
          <p class="game-price">¥{{ formatPrice(game.price) }}</p>
          <div class="purchase-actions">
            <button 
              v-if="!gameStore.isInLibrary(game.id)" 
              @click="handleAddToCart" 
              class="btn-add-cart"
              :disabled="gameStore.isInCart(game.id) || isLoading"
            >
              <span v-if="isLoading">添加中...</span>
              <span v-else>{{ gameStore.isInCart(game.id) ? '已在购物车' : '添加到购物车' }}</span>
            </button>
            <button 
              v-if="gameStore.isInCart(game.id) && !gameStore.isInLibrary(game.id)" 
              @click="goToCart" 
              class="btn-go-cart"
            >
              前往购物车
            </button>
            <button 
              v-if="gameStore.isInLibrary(game.id)" 
              @click="launchGame" 
              class="btn-launch"
            >
              启动游戏
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <div class="back-to-store">
      <button @click="goBack" class="btn-back">« {{ backButtonText }}</button>
    </div>
  </div>
  <div v-else class="loading-container">
    <p>加载中...</p>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGameStore } from '@/stores/gameStore'
import type { Game } from '@/stores/gameStore'
import { formatPrice } from '@/utils/formatters'

export default defineComponent({
  name: 'GameDetailView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const gameStore = useGameStore()
    
    // 确保在组件挂载时加载所有必要的数据
    onMounted(async () => {
      await gameStore.loadGames()
      if (gameStore.libraryGames.length === 0) {
        await gameStore.loadUserLibrary()
      }
    })
    
    const game = computed(() => {
      const gameId = Number(route.params.id)
      // 先从商店游戏列表中查找
      let foundGame = gameStore.games.find(g => g.id === gameId)
      // 如果商店中没有，再从游戏库中查找
      if (!foundGame) {
        foundGame = gameStore.libraryGames.find(g => g.id === gameId)
      }
      return foundGame || null
    })
    
    // 智能返回按钮文本
    const backButtonText = computed(() => {
      if (route.query.from === 'library') {
        return '返回游戏库'
      }
      return '返回商店'
    })
    
    const goToCart = () => {
      router.push('/cart')
    }
    
    const goBack = () => {
      if (route.query.from === 'library') {
        router.push('/library')
      } else {
        router.push('/store')
      }
    }
    
    const isLoading = ref(false)
    
    const handleAddToCart = async () => {
      if (!game.value) return
      
      isLoading.value = true
      try {
        await gameStore.addToCart(game.value)
      } finally {
        isLoading.value = false
      }
    }
    
    const launchGame = () => {
      if (game.value) {
        console.log(`🎮 成功启动游戏: ${game.value.title}`)
        console.log('游戏详情:', {
          id: game.value.id,
          title: game.value.title,
          developer: game.value.developer,
          type: game.value.type
        })
        
        // 可以添加更多的启动逻辑，比如：
        // - 检查游戏是否已安装
        // - 启动游戏进程
        // - 记录游戏启动时间
        // - 显示启动动画等
        
        alert(`正在启动 "${game.value.title}"...\n`)
      }
    }
    
    return {
      game,
      gameStore,
      goToCart,
      goBack,
      backButtonText,
      isLoading,
      handleAddToCart,
      launchGame,
      formatPrice
    }
  }
})
</script>

<style scoped>
.game-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  color: #c7d5e0;
}

.game-detail-header {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
}

.game-image-large {
  flex: 0 0 40%;
}

.game-image-large img {
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
}

.game-header-info {
  flex: 1;
}

.game-title {
  font-size: 2.5rem;
  margin-top: 0;
  margin-bottom: 1rem;
  color: #ffffff;
}

.game-meta {
  margin-bottom: 1.5rem;
}

.game-developer, .game-publisher, .game-release, .game-type {
  margin: 0.5rem 0;
  font-size: 1rem;
  color: #8f98a0;
}

.game-detail-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.game-description-section h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #ffffff;
}

.game-description-full {
  line-height: 1.6;
  color: #c7d5e0;
}

.game-price-card {
  background-color: #2a475e;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.game-price-card h3 {
  margin-top: 0;
  font-size: 1.2rem;
  color: #ffffff;
}

.game-price {
  font-size: 1.8rem;
  font-weight: bold;
  color: #c7d5e0;
  margin: 1rem 0;
}

.purchase-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.btn-add-cart, .btn-go-cart, .btn-launch {
  padding: 0.8rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  text-align: center;
  transition: background-color 0.3s;
}

.btn-add-cart {
  background-color: #5c7e10;
  color: white;
}

.btn-add-cart:hover {
  background-color: #6d9619;
}

.btn-add-cart:disabled {
  background-color: #4a6e0e;
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-go-cart {
  background-color: #1a9fff;
  color: white;
}

.btn-go-cart:hover {
  background-color: #0b8eee;
}

.btn-launch {
  background-color: #27a74a;
  color: white;
}

.btn-launch:hover {
  background-color: #1e8c3a;
}

.back-to-store {
  margin-top: 2rem;
}

.btn-back {
  color: #c7d5e0;
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  transition: color 0.3s;
}

.btn-back:hover {
  color: #ffffff;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 50vh;
  font-size: 1.2rem;
  color: #8f98a0;
}

@media (max-width: 768px) {
  .game-detail-header {
    flex-direction: column;
  }
  
  .game-detail-content {
    grid-template-columns: 1fr;
  }
}
</style>