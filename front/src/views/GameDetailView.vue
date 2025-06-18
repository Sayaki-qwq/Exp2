<template>
  <div class="game-detail-wrapper" v-if="game">
    <!-- 背景层 -->
    <div 
      class="background-layer"
      :style="{ backgroundImage: `url(${game.imageUrl})` }"
    ></div>
    <div class="background-overlay"></div>
    
    <!-- 内容层 -->
    <div class="game-detail-container">
      <div class="game-detail-header">
        <div class="game-image-large">
          <img :src="game.imageUrl" :alt="game.title">
        </div>
        <div class="game-header-info">
          <h1 class="game-title">{{ game.title }}</h1>
          <div class="game-meta">
            <p class="game-developer">
              开发商: 
              <span 
                @click="navigateToDeveloper" 
                class="developer-link"
              >
                {{ game.developer }}
              </span>
            </p>
            <p class="game-publisher">
              发行商: 
              <span 
                @click="navigateToPublisher" 
                class="publisher-link"
              >
                {{ game.publisher }}
              </span>
            </p>
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
          
          <!-- 评分区域 -->
          <div class="game-rating-card">
            <h3>用户评价</h3>
            <div v-if="gameRatings" class="rating-stats">
              <div class="rating-percentage">
                <span class="percentage">{{ gameRatings.like_percentage }}%</span>
                <span class="percentage-label">好评率</span>
              </div>
              <div class="rating-counts">
                <span class="rating-count">
                  👍 {{ gameRatings.like_count }} 个好评
                </span>
                <span class="rating-count">
                  👎 {{ gameRatings.dislike_count }} 个差评
                </span>
                <span class="total-count">
                  总计 {{ gameRatings.total_count }} 个评价
                </span>
              </div>
            </div>
            <div v-else class="no-ratings">
              <p>暂无评价</p>
            </div>
            
            <!-- 用户评分按钮 -->
            <div class="user-rating-actions">
              <h4>您的评价</h4>
              <div class="rating-buttons">
                <button 
                  @click="handleRating('like')"
                  :class="['btn-rating', 'btn-like', { active: userRating?.rating === 'like' }]"
                  :disabled="ratingLoading"
                >
                  👍 喜欢
                </button>
                <button 
                  @click="handleRating('dislike')"
                  :class="['btn-rating', 'btn-dislike', { active: userRating?.rating === 'dislike' }]"
                  :disabled="ratingLoading"
                >
                  👎 不喜欢
                </button>
                <button 
                  v-if="userRating?.rating"
                  @click="handleDeleteRating"
                  class="btn-rating btn-clear"
                  :disabled="ratingLoading"
                >
                  清除评价
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="back-to-store">
        <button @click="goBack" class="btn-back">« {{ backButtonText }}</button>
      </div>
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
import { useUserStore } from '@/stores/userStore'
import type { Game, GameRating, UserRating } from '@/stores/gameStore'
import { formatPrice } from '@/utils/formatters'

export default defineComponent({
  name: 'GameDetailView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const gameStore = useGameStore()
    const userStore = useUserStore()
    
    // 评分相关的响应式数据
    const gameRatings = ref<GameRating | null>(null)
    const userRating = ref<UserRating | null>(null)
    const ratingLoading = ref(false)
    
    // 确保在组件挂载时加载所有必要的数据
    onMounted(async () => {
      await gameStore.loadGames()
      if (gameStore.libraryGames.length === 0) {
        await gameStore.loadUserLibrary()
      }
      
      // 加载评分数据
      const gameId = Number(route.params.id)
      if (gameId) {
        await loadRatingData(gameId)
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
      } else if (route.query.from === 'developer' && route.query.developer) {
        return `返回 ${route.query.developer} 页面`
      } else if (route.query.from === 'publisher' && route.query.publisher) {
        return `返回 ${route.query.publisher} 页面`
      }
      return '返回商店'
    })
    
    const goToCart = () => {
      router.push('/cart')
    }
    
    const goBack = () => {
      if (route.query.from === 'library') {
        router.push('/library')
      } else if (route.query.from === 'developer' && route.query.developer) {
        router.push(`/developer/${encodeURIComponent(route.query.developer as string)}`)
      } else if (route.query.from === 'publisher' && route.query.publisher) {
        router.push(`/publisher/${encodeURIComponent(route.query.publisher as string)}`)
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
        
        alert(`正在启动 "${game.value.title}"...\n`)
      }
    }
    
    const navigateToDeveloper = () => {
      if (game.value?.developer) {
        router.push(`/developer/${encodeURIComponent(game.value.developer)}?from=game&gameId=${game.value.id}`)
      }
    }
    
    const navigateToPublisher = () => {
      if (game.value?.publisher) {
        router.push(`/publisher/${encodeURIComponent(game.value.publisher)}?from=game&gameId=${game.value.id}`)
      }
    }
    
    // 评分相关方法
    const loadRatingData = async (gameId: number) => {
      try {
        // 加载游戏评分统计
        gameRatings.value = await gameStore.getGameRatings(gameId)
        
        // 加载用户评分
        if (userStore.isLoggedIn) {
          userRating.value = await gameStore.getUserRating(gameId)
        }
      } catch (error) {
        console.error('加载评分数据失败', error)
      }
    }
    
    const handleRating = async (rating: 'like' | 'dislike') => {
      if (!game.value) return
      
      ratingLoading.value = true
      try {
        const success = await gameStore.rateGame(game.value.id, rating)
        if (success) {
          // 重新加载评分数据
          await loadRatingData(game.value.id)
        }
      } finally {
        ratingLoading.value = false
      }
    }
    
    const handleDeleteRating = async () => {
      if (!game.value) return
      
      ratingLoading.value = true
      try {
        const success = await gameStore.deleteRating(game.value.id)
        if (success) {
          // 重新加载评分数据
          await loadRatingData(game.value.id)
        }
      } finally {
        ratingLoading.value = false
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
      formatPrice,
      navigateToDeveloper,
      navigateToPublisher,
      // 评分相关
      gameRatings,
      userRating,
      ratingLoading,
      handleRating,
      handleDeleteRating
    }
  }
})
</script>

<style scoped>
.game-detail-wrapper {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  margin: -2rem;
  padding: 2rem;
}

.background-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  filter: blur(80px);
  transform: scale(1.1);
  z-index: 0;
}

.background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1;
}

.game-detail-container {
  position: relative;
  max-width: 1400px;
  margin: 0 auto;
  padding: 2.5rem;
  color: #c7d5e0;
  z-index: 2;
  background: rgba(27, 40, 56, 0.85);
  border-radius: 12px;
  margin-top: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
}

.game-detail-header {
  display: flex;
  gap: 2.5rem;
  margin-bottom: 2.5rem;
}

.game-image-large {
  flex: 0 0 50%;
}

.game-image-large img {
  width: 100%;
  border-radius: 10px;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.6);
  transition: transform 0.3s ease;
}

.game-image-large img:hover {
  transform: scale(1.02);
}

.game-header-info {
  flex: 1;
}

.game-title {
  font-size: 2.5rem;
  margin-top: 0;
  margin-bottom: 1rem;
  color: #ffffff;
  text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.8), 0 0 10px rgba(0, 0, 0, 0.6);
}

.game-meta {
  margin-bottom: 1.5rem;
}

.game-developer, .game-publisher, .game-release, .game-type {
  margin: 0.75rem 0;
  font-size: 1.5rem;
  font-weight: 500;
  color: #f0f0f0;
  text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.7);
}

.developer-link {
  color: #90d000;
  cursor: pointer;
  text-decoration: underline;
  transition: color 0.3s;
  text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.8);
  font-weight: 600;
}

.developer-link:hover {
  color: #b3ff00;
}

.publisher-link {
  color: #90d000;
  cursor: pointer;
  text-decoration: underline;
  transition: color 0.3s;
  text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.8);
  font-weight: 600;
}

.publisher-link:hover {
  color: #b3ff00;
}

.game-detail-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2.5rem;
  margin-bottom: 2.5rem;
}

.game-description-section h2 {
  font-size: 1.8rem;
  margin-bottom: 1.2rem;
  color: #ffffff;
  text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.8);
}

.game-description-full {
  font-size: 1.5rem;
  line-height: 1.7;
  color: #f5f5f5;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.6);
}

.game-price-card {
  background-color: rgba(42, 71, 94, 0.9);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 1.5rem;
}

.game-rating-card {
  background-color: rgba(42, 71, 94, 0.9);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.game-rating-card h3 {
  color: #ffffff;
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

.rating-stats {
  margin-bottom: 1.5rem;
}

.rating-percentage {
  text-align: center;
  margin-bottom: 1rem;
}

.percentage {
  display: block;
  font-size: 3rem;
  font-weight: bold;
  color: #5c7e10;
  text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.6);
  line-height: 1;
}

.percentage-label {
  display: block;
  color: #c7d5e0;
  font-size: 1.2rem;
  font-weight: 500;
  margin-top: 0.5rem;
}

.rating-counts {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  text-align: center;
}

.rating-count, .total-count {
  color: #c7d5e0;
  font-size: 1.2rem;
  font-weight: 500;
}

.total-count {
  color: #8f98a0;
  font-style: italic;
  font-size: 1.2rem;
  margin-top: 0.5rem;
}

.no-ratings {
  text-align: center;
  color: #8f98a0;
  margin-bottom: 1.5rem;
}

.user-rating-actions h4 {
  color: #ffffff;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.rating-buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-rating {
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s;
  min-width: 80px;
}

.btn-like {
  background-color: #5c7e10;
  color: white;
}

.btn-like:hover:not(:disabled) {
  background-color: #6d9619;
}

.btn-like.active {
  background-color: #7ab300;
  box-shadow: 0 0 10px rgba(122, 179, 0, 0.5);
}

.btn-dislike {
  background-color: #c23b22;
  color: white;
}

.btn-dislike:hover:not(:disabled) {
  background-color: #d44726;
}

.btn-dislike.active {
  background-color: #e74c3c;
  box-shadow: 0 0 10px rgba(231, 76, 60, 0.5);
}

.btn-clear {
  background-color: #8f98a0;
  color: white;
}

.btn-clear:hover:not(:disabled) {
  background-color: #7a8794;
}

.btn-rating:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.game-price-card h3 {
  margin-top: 0;
  font-size: 1.2rem;
  color: #ffffff;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.game-price {
  font-size: 1.8rem;
  font-weight: bold;
  color: #ffffff;
  margin: 1rem 0;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
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
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.btn-add-cart {
  background-color: #5c7e10;
  color: white;
}

.btn-add-cart:hover {
  background-color: #6d9619;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
}

.btn-add-cart:disabled {
  background-color: #4a6e0e;
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-go-cart {
  background-color: #1a9fff;
  color: white;
}

.btn-go-cart:hover {
  background-color: #0b8eee;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
}

.btn-launch {
  background-color: #27a74a;
  color: white;
}

.btn-launch:hover {
  background-color: #1e8c3a;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
}

.back-to-store {
  margin-top: 2rem;
}

.btn-back {
  color: #e8e8e8;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  backdrop-filter: blur(5px);
}

.btn-back:hover {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
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
  .game-detail-container {
    margin: 0.5rem;
    padding: 1rem;
  }
  
  .game-detail-header {
    flex-direction: column;
  }
  
  .game-detail-content {
    grid-template-columns: 1fr;
  }
  
  .game-title {
    font-size: 2rem;
  }
}
</style>