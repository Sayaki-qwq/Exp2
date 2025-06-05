<template>
  <div class="store-container">
    <h1>游戏商店</h1>
    
    <!-- 搜索区域 -->
    <div class="search-section">
      <div class="search-box">
        <input 
          v-model="searchInput"
          @input="handleSearch"
          @keyup.enter="handleSearch"
          type="text"
          placeholder="搜索游戏..."
          class="search-input"
        >
        <button 
          v-if="searchInput"
          @click="clearSearch"
          class="clear-btn"
        >
          ✕
        </button>
      </div>
      <div v-if="gameStore.isSearching" class="search-status">
        搜索中...
      </div>
      <div v-else-if="gameStore.searchQuery && gameStore.searchResults.length === 0" class="search-status">
        未找到包含 "{{ gameStore.searchQuery }}" 的游戏
      </div>
      <div v-else-if="gameStore.searchQuery" class="search-status">
        找到 {{ gameStore.searchResults.length }} 个游戏
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
          <p class="game-description">{{ game.description }}</p>
          <div class="game-price-actions">
            <p class="game-price">¥{{ game.price }}</p>
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
    
    // 处理搜索
    const handleSearch = () => {
      gameStore.searchGames(searchInput.value)
    }
    
    // 清空搜索
    const clearSearch = () => {
      searchInput.value = ''
      gameStore.clearSearch()
    }
    
    const handleAddToCart = async (game: any) => {
      if (!userStore.isLoggedIn) {
        router.push('/login')
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
      handleSearch,
      clearSearch
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
  margin: 1rem 0 2rem 0;
}

.search-box {
  position: relative;
  max-width: 500px;
  margin: 0 auto;
}

.search-input {
  width: 100%;
  padding: 0.8rem 1rem;
  padding-right: 3rem;
  border: 2px solid #3c5e73;
  border-radius: 25px;
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

.clear-btn {
  position: absolute;
  right: 0.8rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #8f98a0;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.2rem;
  border-radius: 50%;
  transition: background-color 0.3s;
}

.clear-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.search-status {
  text-align: center;
  margin-top: 0.8rem;
  color: #8f98a0;
  font-size: 0.9rem;
}

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
</style>