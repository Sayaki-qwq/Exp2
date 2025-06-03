<template>
  <div class="store-container">
    <h1>游戏商店</h1>
    
    <div class="game-grid">
      <div 
        v-for="game in gameStore.games" 
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
                @click.stop="gameStore.addToCart(game)" 
                class="btn-add-cart"
                :disabled="gameStore.isInCart(game.id)"
              >
                {{ gameStore.isInCart(game.id) ? '已在购物车' : '添加到购物车' }}
              </button>
              <span v-else class="in-library-badge">已拥有</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '@/stores/gameStore'

export default defineComponent({
  name: 'StoreView',
  setup() {
    const gameStore = useGameStore()
    const router = useRouter()
    
    const navigateToGameDetail = (gameId: number) => {
      router.push(`/game/${gameId}`)
    }
    
    return {
      gameStore,
      navigateToGameDetail
    }
  }
})
</script>

<style scoped>
.store-container {
  padding: 1rem;
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
</style>