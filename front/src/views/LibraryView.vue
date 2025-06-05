<template>
  <div class="library-container">
    <h1>游戏库</h1>
    
    <div v-if="gameStore.libraryGames.length === 0" class="empty-library">
      <p>您的游戏库是空的</p>
      <router-link to="/store" class="btn-go-shopping">前往商店</router-link>
    </div>
    
    <div v-else class="library-grid">
      <div 
        v-for="game in gameStore.libraryGames" 
        :key="game.id" 
        class="library-game"
        @click="navigateToGameDetail(game.id)"
      >
        <div class="game-image">
          <img :src="game.imageUrl" :alt="game.title" @error="handleImageError">
        </div>
        <div class="game-info">
          <h2 class="game-title">{{ game.title }}</h2>
          <p class="game-type">类型: {{ game.type }}</p>
          <p class="game-developer">开发商: {{ game.developer }}</p>
          <p class="game-publisher">发行商: {{ game.publisher }}</p>
          <p class="game-description">{{ game.description }}</p>
          <button 
            @click.stop="launchGame(game)" 
            class="btn-install"
          >
            启动游戏
          </button>
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
import type { Game } from '@/stores/gameStore'

export default defineComponent({
  name: 'LibraryView',
  setup() {
    const gameStore = useGameStore()
    const userStore = useUserStore()
    const router = useRouter()
    
    // 在组件挂载时加载游戏库数据
    onMounted(async () => {
      if (!userStore.isLoggedIn) {
        router.push('/login')
        return
      }
      await gameStore.loadUserLibrary()
    })
    
    // 处理图片加载错误
    const handleImageError = (event: Event) => {
      const img = event.target as HTMLImageElement
      img.src = 'https://via.placeholder.com/300x150?text=No+Image'
    }
    
    // 跳转到游戏详细页面
    const navigateToGameDetail = (gameId: number) => {
      router.push(`/game/${gameId}?from=library`)
    }
    
    // 启动游戏功能
    const launchGame = (game: Game) => {
      // 这里可以添加实际的游戏启动逻辑
      // 目前先显示一个提示
      alert(`正在启动 "${game.title}"...`)
    }
    
    return {
      gameStore,
      handleImageError,
      navigateToGameDetail,
      launchGame
    }
  }
})
</script>

<style scoped>
.library-container {
  padding: 1rem;
}

.empty-library {
  text-align: center;
  margin-top: 3rem;
}

.btn-go-shopping {
  display: inline-block;
  background-color: #5c7e10;
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  margin-top: 1rem;
  transition: background-color 0.3s;
}

.btn-go-shopping:hover {
  background-color: #6d9619;
}

.library-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.library-game {
  background-color: #2a475e;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  cursor: pointer;
}

.library-game:hover {
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

.game-type, .game-developer, .game-publisher {
  margin: 0.3rem 0;
  font-size: 0.85rem;
  color: #8f98a0;
}

.game-description {
  margin: 0.5rem 0;
  font-size: 0.9rem;
  color: #c7d5e0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.btn-install {
  background-color: #1a9fff;
  color: white;
  border: none;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  width: 100%;
  margin-top: 0.5rem;
  font-size: 0.9rem;
  transition: background-color 0.3s;
}

.btn-install:hover {
  background-color: #0b8eee;
}
</style>