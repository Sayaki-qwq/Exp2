<template>
  <div class="developer-container">
    <div class="developer-header">
      <h1>{{ developerName }}</h1>
      <p class="developer-subtitle">开发的游戏</p>
    </div>
    
    <div v-if="isLoading" class="loading-container">
      <p>加载中...</p>
    </div>
    
    <div v-else-if="developerGames.length === 0" class="no-games">
      <p>该开发商暂无游戏</p>
      <button @click="goBack" class="btn-back">返回</button>
    </div>
    
    <div v-else class="games-grid">
      <div 
        v-for="game in developerGames" 
        :key="game.id" 
        class="game-card"
        @click="navigateToGameDetail(game.id)"
      >
        <div class="game-image">
          <img :src="game.imageUrl" :alt="game.title" @error="handleImageError">
        </div>
        <div class="game-info">
          <h2 class="game-title">{{ game.title }}</h2>
          <p class="game-type">类型: {{ game.type }}</p>
          <p class="game-publisher">发行商: {{ game.publisher }}</p>
          <p class="game-release">发行日期: {{ game.releaseDate }}</p>
          <p class="game-description">{{ game.description }}</p>
          <div class="game-price-actions">
            <p class="game-price">¥{{ formatPrice(game.price) }}</p>
            <div class="game-actions">
              <button 
                v-if="!gameStore.isInLibrary(game.id)" 
                @click.stop="handleAddToCart(game)" 
                class="btn-add-cart"
                :disabled="gameStore.isInCart(game.id) || isLoading"
              >
                <span v-if="isLoading && loadingGameId === game.id">添加中...</span>
                <span v-else>{{ gameStore.isInCart(game.id) ? '已在购物车' : '添加到购物车' }}</span>
              </button>
              <span v-else class="in-library-badge">已拥有</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="back-navigation">
      <button @click="goBack" class="btn-back">« 返回</button>
    </div>
    
    <!-- 提示消息 -->
    <div v-if="showMessage" :class="['message', messageType]">
      {{ message }}
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGameStore } from '@/stores/gameStore'
import { useUserStore } from '@/stores/userStore'
import type { Game } from '@/stores/gameStore'
import { formatPrice } from '@/utils/formatters'

export default defineComponent({
  name: 'DeveloperView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const gameStore = useGameStore()
    const userStore = useUserStore()
    
    const isLoading = ref(true)
    const loadingGameId = ref<number | null>(null)
    const showMessage = ref(false)
    const message = ref('')
    const messageType = ref('')
    
    const developerName = computed(() => route.params.name as string)
    
    // 根据开发商筛选游戏
    const developerGames = computed(() => {
      if (!developerName.value) return []
      return gameStore.games.filter(game => 
        game.developer === developerName.value
      )
    })
    
    // 显示提示消息
    const showToast = (msg: string, type: 'success' | 'error') => {
      message.value = msg
      messageType.value = type
      showMessage.value = true
      setTimeout(() => {
        showMessage.value = false
      }, 3000)
    }
    
    // 在组件挂载时加载游戏数据
    onMounted(async () => {
      try {
        await gameStore.loadGames()
        await gameStore.loadUserLibrary()
        await gameStore.loadUserCart()
      } finally {
        isLoading.value = false
      }
    })
    
    // 处理图片加载错误
    const handleImageError = (event: Event) => {
      const img = event.target as HTMLImageElement
      img.src = 'https://via.placeholder.com/300x150?text=No+Image'
    }
    
    // 跳转到游戏详细页面
    const navigateToGameDetail = (gameId: number) => {
      router.push(`/game/${gameId}?from=developer&developer=${encodeURIComponent(developerName.value)}`)
    }
    
    // 返回上一页
    const goBack = () => {
      if (route.query.from && route.query.gameId) {
        router.push(`/game/${route.query.gameId}`)
      } else {
        router.push('/store')
      }
    }
    
    // 添加到购物车
    const handleAddToCart = async (game: Game) => {
      if (!userStore.isLoggedIn) {
        alert('请先登录')
        return
      }

      try {
        isLoading.value = true
        loadingGameId.value = game.id
        const success = await gameStore.addToCart(game)
        
        if (success) {
          showToast('成功添加到购物车', 'success')
        } else {
          showToast('添加失败，请重试', 'error')
        }
      } catch (error) {
        showToast('添加失败，请重试', 'error')
      } finally {
        isLoading.value = false
        loadingGameId.value = null
      }
    }
    
    return {
      developerName,
      developerGames,
      gameStore,
      isLoading,
      loadingGameId,
      showMessage,
      message,
      messageType,
      navigateToGameDetail,
      goBack,
      handleAddToCart,
      handleImageError,
      formatPrice
    }
  }
})
</script>

<style scoped>
.developer-container {
  padding: 1rem;
  position: relative;
}

.developer-header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 2rem 0;
  background: linear-gradient(135deg, #2a475e 0%, #1b2838 100%);
  border-radius: 8px;
  margin-bottom: 2rem;
}

.developer-header h1 {
  font-size: 2.5rem;
  margin: 0 0 0.5rem 0;
  color: #ffffff;
}

.developer-subtitle {
  font-size: 1.2rem;
  color: #8f98a0;
  margin: 0;
}

.loading-container, .no-games {
  text-align: center;
  margin-top: 3rem;
  color: #8f98a0;
}

.no-games p {
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.games-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.game-card {
  background-color: #2a475e;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  cursor: pointer;
}

.game-card:hover {
  transform: translateY(-5px);
}

.game-image img {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.game-info {
  padding: 1rem;
}

.game-title {
  margin-top: 0;
  font-size: 1.2rem;
  color: #ffffff;
  margin-bottom: 0.5rem;
}

.game-type, .game-publisher, .game-release {
  margin: 0.5rem 0;
  font-size: 0.9rem;
  color: #8f98a0;
}

.game-description {
  font-size: 0.9rem;
  color: #c7d5e0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0.5rem 0;
}

.game-price-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.game-price {
  font-size: 1.2rem;
  font-weight: bold;
  color: #c7d5e0;
  margin: 0;
}

.btn-add-cart {
  background-color: #5c7e10;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s;
  min-width: 100px;
}

.btn-add-cart:hover {
  background-color: #6d9619;
}

.btn-add-cart:disabled {
  background-color: #4a6e0e;
  opacity: 0.7;
  cursor: not-allowed;
}

.in-library-badge {
  background-color: #1a9fff;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
}

.back-navigation {
  margin-top: 2rem;
  text-align: center;
}

.btn-back {
  color: #c7d5e0;
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  transition: color 0.3s;
  padding: 0.5rem 1rem;
}

.btn-back:hover {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

/* 提示消息样式 */
.message {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 10px 20px;
  border-radius: 4px;
  color: white;
  z-index: 1000;
  animation: fadeInOut 3s ease-in-out;
}

.success {
  background-color: #5c7e10;
}

.error {
  background-color: #c23b22;
}

@keyframes fadeInOut {
  0% {
    opacity: 0;
    transform: translate(-50%, 20px);
  }
  10% {
    opacity: 1;
    transform: translate(-50%, 0);
  }
  90% {
    opacity: 1;
    transform: translate(-50%, 0);
  }
  100% {
    opacity: 0;
    transform: translate(-50%, -20px);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .developer-header h1 {
    font-size: 2rem;
  }
  
  .games-grid {
    grid-template-columns: 1fr;
  }
}
</style> 