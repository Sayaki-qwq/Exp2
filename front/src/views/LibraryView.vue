<template>
  <div class="library-container">
    <h1>游戏库</h1>
    
    <div v-if="gameStore.libraryGames.length === 0" class="empty-library">
      <p>您的游戏库是空的</p>
      <router-link to="/store" class="btn-go-shopping">前往商店</router-link>
    </div>
    
    <div v-else class="library-grid">
      <div v-for="game in gameStore.libraryGames" :key="game.id" class="library-game">
        <div class="game-image">
          <img :src="game.imageUrl" :alt="game.title">
        </div>
        <div class="game-info">
          <h2 class="game-title">{{ game.title }}</h2>
          <p class="game-developer">{{ game.developer }}</p>
          <button class="btn-install">安装</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useGameStore } from '@/stores/gameStore'

export default defineComponent({
  name: 'LibraryView',
  setup() {
    const gameStore = useGameStore()
    
    return {
      gameStore
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
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.library-game {
  background-color: #2a475e;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s;
}

.library-game:hover {
  transform: translateY(-5px);
}

.game-image img {
  width: 100%;
  height: 120px;
  object-fit: cover;
}

.game-info {
  padding: 1rem;
}

.game-title {
  margin-top: 0;
  font-size: 1.1rem;
  color: #ffffff;
}

.game-developer {
  margin: 0.5rem 0;
  font-size: 0.9rem;
  color: #8f98a0;
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