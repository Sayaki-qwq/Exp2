<template>
  <div class="store-container">
    <h1>游戏商店</h1>
    
    <!-- 搜索框 -->
    <div class="search-section">
      <div class="search-bar">
        <input 
          v-model="searchInput"
          @input="handleSearchInput"
          @keyup.enter="performSearch"
          type="text" 
          placeholder="搜索游戏标题..."
          class="search-input"
        >
        <button 
          @click="performSearch"
          :disabled="gameStore.isSearching"
          class="search-button"
        >
          <span v-if="gameStore.isSearching">搜索中...</span>
          <span v-else>搜索</span>
        </button>
        <button 
          v-if="gameStore.searchQuery"
          @click="clearSearch"
          class="clear-button"
        >
          清空
        </button>
      </div>
      
      <!-- 排序选择器 -->
      <div class="sort-section">
        <div class="sort-controls">
          <label class="sort-label">排序方式：</label>
          <select 
            v-model="gameStore.sortBy" 
            @change="handleSortChange"
            class="sort-select"
          >
            <option value="default">默认</option>
            <option value="release_date">发行日期</option>
            <option value="price">价格</option>
            <option value="like_percentage">好评率</option>
          </select>
          
          <label class="sort-label order-label">排序：</label>
          <select 
            v-model="gameStore.sortOrder"
            @change="handleSortOrderChange"
            class="sort-select"
            :disabled="gameStore.sortBy === 'default'"
          >
            <option value="desc">{{ getSortOrderText(gameStore.sortBy, 'desc') }}</option>
            <option value="asc">{{ getSortOrderText(gameStore.sortBy, 'asc') }}</option>
          </select>
        </div>
      </div>
      
      <!-- 搜索状态显示 -->
      <div v-if="gameStore.searchQuery" class="search-status">
        <p>搜索 "{{ gameStore.searchQuery }}" 的结果：共找到 {{ gameStore.displayGames.length }} 个游戏</p>
      </div>
    </div>
    
    <div class="game-grid">
      <div 
        v-for="game in gameStore.displayGames" 
        :key="game.id" 
        class="game-card"
        @click="navigateToGameDetail(game.id)"
      >
        <div class="game-image">
          <img :src="game.imageUrl" :alt="game.title">
        </div>
        <div class="game-info">
          <h2 class="game-title">{{ game.title }}</h2>
          <p class="game-type">类型: {{ game.type }}</p>
          <p class="game-developer">开发商: {{ game.developer }}</p>
          <p class="game-publisher">发行商: {{ game.publisher }}</p>
          <p class="game-release">发行日期: {{ game.releaseDate }}</p>
          <div class="game-rating">
            <span class="rating-label">好评率:</span>
            <span class="rating-percentage" :class="{ 'no-rating': game.likePercentage === 0 }">
              {{ game.likePercentage === 0 ? '暂无评价' : `${game.likePercentage}%` }}
            </span>
          </div>
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

    <!-- 空搜索结果提示 -->
    <div v-if="gameStore.searchQuery && gameStore.displayGames.length === 0 && !gameStore.isSearching" class="no-results">
      <p>没有找到与 "{{ gameStore.searchQuery }}" 相关的游戏</p>
      <button @click="clearSearch" class="btn-clear-search">查看所有游戏</button>
    </div>

    <!-- 提示消息 -->
    <div v-if="showMessage" :class="['message', messageType]">
      {{ message }}
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '@/stores/gameStore'
import { useUserStore } from '@/stores/userStore'
import { formatPrice } from '@/utils/formatters'

export default defineComponent({
  name: 'StoreView',
  setup() {
    const gameStore = useGameStore()
    const userStore = useUserStore()
    const router = useRouter()
    
    const isLoading = ref(false)
    const loadingGameId = ref<number | null>(null)
    const showMessage = ref(false)
    const message = ref('')
    const messageType = ref('')
    const searchInput = ref('')

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
      await gameStore.loadGames()
    })
    
    // 处理搜索输入
    const handleSearchInput = () => {
      // 可以添加防抖逻辑
      if (!searchInput.value.trim()) {
        gameStore.clearSearch()
      }
    }
    
    // 执行搜索
    const performSearch = () => {
      gameStore.searchGames(searchInput.value)
    }
    
    // 清空搜索
    const clearSearch = () => {
      searchInput.value = ''
      gameStore.clearSearch()
    }
    
    const handleAddToCart = async (game: any) => {
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
    
    const navigateToGameDetail = (gameId: number) => {
      router.push(`/game/${gameId}`)
    }
    
    // 处理排序方式变化
    const handleSortChange = () => {
      // Vue的响应式系统会自动处理，无需额外操作
    }
    
    // 处理排序顺序变化
    const handleSortOrderChange = () => {
      // Vue的响应式系统会自动处理，无需额外操作
    }
    
    // 获取排序顺序的显示文本
    const getSortOrderText = (sortBy: string, order: string) => {
      if (sortBy === 'release_date') {
        return order === 'desc' ? '最新' : '最早'
      } else if (sortBy === 'price') {
        return order === 'desc' ? '降序' : '升序'
      } else if (sortBy === 'like_percentage') {
        return order === 'desc' ? '高到低' : '低到高'
      }
      return '默认'
    }
    
    return {
      gameStore,
      navigateToGameDetail,
      handleAddToCart,
      isLoading,
      loadingGameId,
      showMessage,
      message,
      messageType,
      searchInput,
      handleSearchInput,
      performSearch,
      clearSearch,
      handleSortChange,
      handleSortOrderChange,
      getSortOrderText,
      formatPrice
    }
  }
})
</script>

<style scoped>
.store-container {
  padding: 1rem;
  position: relative;
}

/* 搜索区域样式 */
.search-section {
  margin-bottom: 2rem;
}

.search-bar {
  display: flex;
  gap: 0.5rem;
  max-width: 600px;
  margin: 0 auto 1rem auto;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #387198;
  border-radius: 4px;
  background-color: #1b2838;
  color: #c7d5e0;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: #5c7e10;
}

.search-input::placeholder {
  color: #8f98a0;
}

.search-button, .clear-button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s;
}

.search-button {
  background-color: #5c7e10;
  color: white;
  min-width: 80px;
}

.search-button:hover:not(:disabled) {
  background-color: #6d9619;
}

.search-button:disabled {
  background-color: #4a6e0e;
  opacity: 0.7;
  cursor: not-allowed;
}

.clear-button {
  background-color: #8f98a0;
  color: white;
}

.clear-button:hover {
  background-color: #7a8794;
}

.search-status {
  text-align: center;
  color: #c7d5e0;
  font-size: 1.1rem;
  font-weight: 500;
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: rgba(42, 71, 94, 0.3);
  border-radius: 6px;
}

.search-status p {
  margin: 0;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

/* 排序区域样式 */
.sort-section {
  margin-top: 1rem;
}

.sort-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.sort-label {
  color: #c7d5e0;
  font-size: 0.9rem;
  font-weight: 500;
}

.order-label {
  margin-left: 1rem;
}

.sort-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #387198;
  border-radius: 4px;
  background-color: #1b2838;
  color: #c7d5e0;
  font-size: 0.9rem;
  outline: none;
  cursor: pointer;
  transition: border-color 0.3s;
}

.sort-select:focus {
  border-color: #5c7e10;
}

.sort-select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #0f1419;
}

.sort-select option {
  background-color: #1b2838;
  color: #c7d5e0;
}

/* 空搜索结果样式 */
.no-results {
  text-align: center;
  margin-top: 3rem;
  color: #8f98a0;
}

.no-results p {
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.btn-clear-search {
  background-color: #5c7e10;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s;
}

.btn-clear-search:hover {
  background-color: #6d9619;
}

/* 其他现有样式保持不变 */
.game-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
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
}

 .game-type, .game-developer, .game-publisher, .game-release {
   margin: 0.5rem 0;
   font-size: 0.9rem;
   color: #8f98a0;
 }
 
 .game-rating {
   margin: 0.5rem 0;
   display: flex;
   align-items: center;
   gap: 0.5rem;
 }
 
 .rating-label {
   font-size: 0.9rem;
   color: #8f98a0;
 }
 
 .rating-percentage {
   font-size: 0.9rem;
   font-weight: 600;
   color: #90d000;
   background-color: rgba(144, 208, 0, 0.15);
   padding: 0.2rem 0.5rem;
   border-radius: 4px;
   border: 1px solid rgba(144, 208, 0, 0.3);
 }
 
 .rating-percentage.no-rating {
   color: #8f98a0;
   background-color: rgba(143, 152, 160, 0.15);
   border-color: rgba(143, 152, 160, 0.3);
 }

.game-description {
  font-size: 0.9rem;
  color: #c7d5e0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
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
  .search-bar {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .search-button, .clear-button {
    width: 100%;
  }
  
  .sort-controls {
    flex-direction: column;
    gap: 0.5rem;
    align-items: stretch;
  }
  
  .sort-label {
    text-align: center;
  }
  
  .order-label {
    margin-left: 0;
  }
  
  .sort-select {
    width: 100%;
  }
}
</style>