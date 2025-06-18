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
          </div>
        </div>
      </div>
      
      <!-- 用户评论表单区域 (独立占用一行) -->
      <div v-if="userStore.isLoggedIn && gameStore.isInLibrary(game.id)" class="review-form-section">
        <div class="user-review-form-full">
          <h3>{{ userRating?.rating ? '修改您的评论' : '发表您的评论' }}</h3>
          <div class="review-form">
            <div class="rating-selection">
              <label>
                <input 
                  type="radio" 
                  name="rating" 
                  value="like" 
                  v-model="newReviewRating"
                >
                👍 推荐这款游戏
              </label>
              <label>
                <input 
                  type="radio" 
                  name="rating" 
                  value="dislike" 
                  v-model="newReviewRating"
                >
                👎 不推荐这款游戏
              </label>
            </div>
            <textarea 
              v-model="newReviewComment"
              placeholder="分享您的游戏体验，让其他玩家了解这款游戏的优缺点..."
              maxlength="1000"
              rows="5"
              class="review-textarea"
            ></textarea>
            <div class="review-form-footer">
              <div class="character-count">
                {{ newReviewComment.length }}/1000 字符
              </div>
              <div class="review-actions">
                <button 
                  @click="handleSubmitReview"
                  :disabled="!newReviewRating || !newReviewComment.trim() || reviewLoading"
                  class="btn-submit-review"
                >
                  {{ reviewLoading ? '提交中...' : (userRating?.rating ? '修改评论' : '发表评论') }}
                </button>
                <button 
                  v-if="userRating?.rating"
                  @click="handleDeleteReview"
                  :disabled="reviewLoading"
                  class="btn-delete-review"
                >
                  删除评论
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
             <!-- 未登录用户的登录提示区域 -->
       <div v-else-if="!userStore.isLoggedIn" class="login-prompt-section">
         <div class="login-prompt-card">
           <h3>分享您的游戏体验</h3>
           <div class="login-prompt-content">
             <div class="prompt-icon">🎮</div>
             <div class="prompt-text">
               <p class="main-text">想要发表评论和评分吗？</p>
               <p class="sub-text">登录后即可分享您的游戏体验，帮助其他玩家做出选择</p>
             </div>
           </div>
         </div>
       </div>
      
      <!-- 已登录但未拥有游戏的用户提示 -->
      <div v-else-if="userStore.isLoggedIn && !gameStore.isInLibrary(game.id)" class="purchase-prompt-section">
        <div class="purchase-prompt-card">
          <h3>发表详细评论</h3>
          <div class="purchase-prompt-content">
            <div class="prompt-icon">🛒</div>
            <div class="prompt-text">
              <p class="main-text">拥有游戏后可发表评论</p>
              <p class="sub-text">购买这款游戏后，您就可以分享详细的游戏体验和评价了</p>
            </div>
          </div>
          <div class="purchase-prompt-actions">
            <button 
              @click="handleAddToCart"
              :disabled="gameStore.isInCart(game.id) || isLoading"
              class="btn-add-to-cart-prompt"
            >
              <span v-if="isLoading">添加中...</span>
              <span v-else>{{ gameStore.isInCart(game.id) ? '已在购物车' : '添加到购物车' }}</span>
            </button>
            <button 
              v-if="gameStore.isInCart(game.id)"
              @click="goToCart" 
              class="btn-go-to-cart-prompt"
            >
              前往购物车
            </button>
          </div>
                 </div>
       </div>
      
      <!-- 游戏评论区域 -->
      <div class="game-reviews-section">
        <h2>玩家评论</h2>
        <div v-if="gameReviews.length > 0" class="reviews-list">
          <div 
            v-for="review in gameReviews" 
            :key="review.id"
            class="review-item"
          >
            <div class="review-header">
              <div class="review-user-info">
                <span class="review-username">{{ review.username }}</span>
                <span :class="['review-rating', review.rating]">
                  {{ review.rating === 'like' ? '👍 推荐' : '👎 不推荐' }}
                </span>
              </div>
              <div class="review-date">
                {{ formatReviewDate(review.created_at) }}
                <span v-if="review.created_at !== review.updated_at" class="edited-label">
                  (已编辑)
                </span>
              </div>
            </div>
            <div class="review-content">
              {{ review.comment }}
            </div>
          </div>
        </div>
        <div v-else class="no-reviews">
          <p>暂无评论</p>
          <p v-if="!userStore.isLoggedIn">成为第一个评论的玩家吧！</p>
          <p v-else-if="!gameStore.isInLibrary(game.id)">购买游戏后即可发表评论</p>
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
import type { Game, GameRating, UserRating, GameReview } from '@/stores/gameStore'
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
    
    // 评论相关的响应式数据
    const gameReviews = ref<GameReview[]>([])
    const reviewLoading = ref(false)
    const newReviewRating = ref<'like' | 'dislike' | ''>('')
    const newReviewComment = ref('')
    
    // 确保在组件挂载时加载所有必要的数据
    onMounted(async () => {
      await gameStore.loadGames()
      if (gameStore.libraryGames.length === 0) {
        await gameStore.loadUserLibrary()
      }
      
      // 加载评分和评论数据
      const gameId = Number(route.params.id)
      if (gameId) {
        await loadRatingData(gameId)
        await loadReviewData(gameId)
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
    
    // 评论相关方法
    const loadReviewData = async (gameId: number) => {
      try {
        gameReviews.value = await gameStore.getGameReviews(gameId)
      } catch (error) {
        console.error('加载评论数据失败', error)
      }
    }
    
    const handleSubmitReview = async () => {
      if (!game.value || !newReviewRating.value || !newReviewComment.value.trim()) return
      
      reviewLoading.value = true
      try {
        const success = await gameStore.addReview(
          game.value.id, 
          newReviewRating.value as 'like' | 'dislike', 
          newReviewComment.value.trim()
        )
        if (success) {
          // 重新加载数据
          await loadRatingData(game.value.id)
          await loadReviewData(game.value.id)
          // 清空表单
          newReviewRating.value = ''
          newReviewComment.value = ''
        }
      } finally {
        reviewLoading.value = false
      }
    }
    
    const handleDeleteReview = async () => {
      if (!game.value) return
      
      reviewLoading.value = true
      try {
        const success = await gameStore.deleteReview(game.value.id)
        if (success) {
          // 重新加载数据
          await loadRatingData(game.value.id)
          await loadReviewData(game.value.id)
          // 清空表单
          newReviewRating.value = ''
          newReviewComment.value = ''
        }
      } finally {
        reviewLoading.value = false
      }
    }
    
    const formatReviewDate = (dateString: string) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    // 在用户评分变化时更新表单
    const updateReviewForm = () => {
      if (userRating.value?.rating) {
        newReviewRating.value = userRating.value.rating
        newReviewComment.value = userRating.value.comment || ''
      }
    }
    

    
    return {
      game,
      gameStore,
      userStore,
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
      handleDeleteRating,
      // 评论相关
      gameReviews,
      reviewLoading,
      newReviewRating,
      newReviewComment,
      handleSubmitReview,
      handleDeleteReview,
      formatReviewDate,
      updateReviewForm
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

/* 评论表单样式 */
.review-form-section {
  margin: 2.5rem 0;
}

.user-review-form-full {
  background-color: rgba(42, 71, 94, 0.9);
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  transition: all 0.3s ease;
}

.user-review-form-full:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5);
  border-color: rgba(255, 255, 255, 0.2);
}

.user-review-form-full h3 {
  color: #ffffff;
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.4rem;
  text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.8);
  text-align: center;
}

.user-review-form {
  background-color: rgba(42, 71, 94, 0.9);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.user-review-form h4 {
  color: #ffffff;
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.review-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.rating-selection {
  display: flex;
  gap: 2rem;
  justify-content: center;
  padding: 1rem;
  background-color: rgba(27, 40, 56, 0.6);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.rating-selection label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #c7d5e0;
  cursor: pointer;
  font-size: 1.1rem;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.rating-selection label:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.rating-selection input[type="radio"] {
  margin: 0;
}

.review-textarea {
  width: 100%;
  min-height: 120px;
  padding: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background-color: rgba(27, 40, 56, 0.8);
  color: #c7d5e0;
  font-size: 1rem;
  line-height: 1.6;
  resize: vertical;
  font-family: inherit;
  transition: all 0.3s ease;
}

.review-textarea:focus {
  outline: none;
  border-color: #5c7e10;
  box-shadow: 0 0 0 3px rgba(92, 126, 16, 0.3);
  background-color: rgba(27, 40, 56, 0.9);
}

.review-textarea::placeholder {
  color: #8f98a0;
  font-style: italic;
}

.review-form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.5rem;
}

.review-actions {
  display: flex;
  gap: 1rem;
}

.btn-submit-review {
  background-color: #5c7e10;
  color: white;
  border: none;
  padding: 0.8rem 2rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.btn-submit-review:hover:not(:disabled) {
  background-color: #6d9619;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
}

.btn-submit-review:disabled {
  background-color: #4a6e0e;
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-delete-review {
  background-color: #c23b22;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.btn-delete-review:hover:not(:disabled) {
  background-color: #d44726;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
}

.btn-delete-review:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.character-count {
  font-size: 0.9rem;
  color: #8f98a0;
  font-weight: 500;
  padding: 0.5rem;
  background-color: rgba(27, 40, 56, 0.6);
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.purchase-hint {
  font-size: 0.9rem;
  color: #8f98a0;
  margin-bottom: 1rem;
  font-style: italic;
}

/* 评论列表样式 */
.game-reviews-section {
  margin-top: 2.5rem;
}

.game-reviews-section h2 {
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
  color: #ffffff;
  text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.8);
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.review-item {
  background-color: rgba(42, 71, 94, 0.7);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.review-user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.review-username {
  font-weight: 600;
  color: #ffffff;
  font-size: 1rem;
}

.review-rating {
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.review-rating.like {
  background-color: rgba(92, 126, 16, 0.3);
  color: #90d000;
  border: 1px solid rgba(144, 208, 0, 0.5);
}

.review-rating.dislike {
  background-color: rgba(194, 59, 34, 0.3);
  color: #ff6b6b;
  border: 1px solid rgba(255, 107, 107, 0.5);
}

.review-date {
  color: #8f98a0;
  font-size: 0.85rem;
  text-align: right;
}

.edited-label {
  font-style: italic;
  color: #7a8794;
  font-size: 0.8rem;
}

.review-content {
  color: #e8e8e8;
  line-height: 1.6;
  font-size: 0.95rem;
  white-space: pre-line;
}

.no-reviews {
  text-align: center;
  color: #8f98a0;
  font-style: italic;
  padding: 2rem;
  font-size: 1.2rem;
}

.no-reviews p {
  margin: 0.5rem 0;
}

/* 登录提示区域样式 */
.login-prompt-section,
.purchase-prompt-section {
  margin: 2.5rem 0;
}

.login-prompt-card,
.purchase-prompt-card {
  background-color: rgba(42, 71, 94, 0.9);
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  transition: all 0.3s ease;
  text-align: center;
}

.login-prompt-card:hover,
.purchase-prompt-card:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5);
  border-color: rgba(255, 255, 255, 0.2);
}

.login-prompt-card h3,
.purchase-prompt-card h3 {
  color: #ffffff;
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.4rem;
  text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.8);
}

.login-prompt-content,
.purchase-prompt-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.prompt-icon {
  font-size: 3rem;
  opacity: 0.8;
}

.prompt-text {
  text-align: left;
}

.main-text {
  font-size: 1.2rem;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 0.5rem 0;
}

.sub-text {
  font-size: 1rem;
  color: #c7d5e0;
  margin: 0;
  line-height: 1.4;
}

.purchase-prompt-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn-add-to-cart-prompt,
.btn-go-to-cart-prompt {
  padding: 0.8rem 2rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  min-width: 140px;
}

.btn-add-to-cart-prompt {
  background-color: #5c7e10;
  color: white;
}

.btn-add-to-cart-prompt:hover:not(:disabled) {
  background-color: #6d9619;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
}

.btn-add-to-cart-prompt:disabled {
  background-color: #4a6e0e;
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-go-to-cart-prompt {
  background-color: #1a9fff;
  color: white;
}

.btn-go-to-cart-prompt:hover {
  background-color: #0b8eee;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
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
  
  .review-header {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
  
  .review-user-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .rating-selection {
    flex-direction: column;
    gap: 0.75rem;
    padding: 0.75rem;
  }
  
  .review-actions {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .review-form-footer {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .character-count {
    text-align: center;
  }
  
  .user-review-form-full {
    padding: 1.5rem;
  }
  
  .user-review-form-full h3 {
    font-size: 1.2rem;
  }
  
  .login-prompt-content,
  .purchase-prompt-content {
    flex-direction: column;
    gap: 1rem;
  }
  
  .prompt-text {
    text-align: center;
  }
  
  .purchase-prompt-actions {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .login-prompt-card,
  .purchase-prompt-card {
    padding: 1.5rem;
  }
}
</style>