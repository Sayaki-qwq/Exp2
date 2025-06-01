<template>
  <div class="game-store">
    <!-- 顶部工具栏 -->
    <div class="store-header">
      <div class="search-section">
        <input 
          type="text" 
          v-model="searchQuery"
          placeholder="搜索游戏..."
          class="search-input"
        >
        <button class="search-btn">🔍</button>
      </div>
      
      <div class="filter-section">
        <select v-model="sortBy" class="filter-select">
          <option value="title">按标题排序</option>
          <option value="price">按价格排序</option>
          <option value="releaseDate">按发行日期排序</option>
        </select>
        <select v-model="priceFilter" class="filter-select">
          <option value="all">全部价格</option>
          <option value="free">免费游戏</option>
          <option value="under50">50元以下</option>
          <option value="under100">100元以下</option>
        </select>
      </div>
    </div>

    <!-- 游戏列表 -->
    <div class="games-grid">
      <div 
        v-for="game in filteredGames" 
        :key="game.id"
        class="game-card"
        @click="viewGameDetails(game)"
      >
        <!-- 游戏封面 -->
        <div class="game-image">
          <img :src="game.coverImage" :alt="game.title" />
          <div class="price-tag">
            <span v-if="game.price === 0" class="free-price">免费</span>
            <span v-else class="price">¥{{ game.price }}</span>
          </div>
        </div>

        <!-- 游戏信息 -->
        <div class="game-info">
          <h3 class="game-title">{{ game.title }}</h3>
          <p class="game-description">{{ truncateText(game.description, 100) }}</p>
          
          <div class="game-details">
            <div class="detail-row">
              <span class="label">发行日期:</span>
              <span class="value">{{ formatDate(game.releaseDate) }}</span>
            </div>
            <div class="detail-row">
              <span class="label">开发者:</span>
              <span class="value">{{ game.developer }}</span>
            </div>
            <div class="detail-row">
              <span class="label">发行商:</span>
              <span class="value">{{ game.publisher }}</span>
            </div>
          </div>

          <div class="game-actions">
            <button 
              class="btn btn-primary"
              @click.stop="addToCart(game)"
              :disabled="game.inCart"
            >
              {{ game.inCart ? '已在购物车' : '加入购物车' }}
            </button>
            <button 
              class="btn btn-secondary"
              @click.stop="addToWishlist(game)"
            >
              {{ game.inWishlist ? '❤️' : '🤍' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载更多 -->
    <div class="load-more" v-if="hasMoreGames">
      <button class="btn btn-outline" @click="loadMoreGames">
        加载更多游戏
      </button>
    </div>

    <!-- 游戏详情弹窗 -->
    <div class="modal-overlay" v-if="selectedGame" @click="closeGameDetails">
      <div class="game-detail-modal" @click.stop>
        <button class="close-btn" @click="closeGameDetails">×</button>
        <div class="modal-content">
          <div class="modal-image">
            <img :src="selectedGame.coverImage" :alt="selectedGame.title" />
          </div>
          <div class="modal-info">
            <h2>{{ selectedGame.title }}</h2>
            <p class="full-description">{{ selectedGame.description }}</p>
            <div class="detail-grid">
              <div class="detail-item">
                <strong>发行日期:</strong> {{ formatDate(selectedGame.releaseDate) }}
              </div>
              <div class="detail-item">
                <strong>开发者:</strong> {{ selectedGame.developer }}
              </div>
              <div class="detail-item">
                <strong>发行商:</strong> {{ selectedGame.publisher }}
              </div>
              <div class="detail-item">
                <strong>价格:</strong> 
                <span v-if="selectedGame.price === 0" class="free-price">免费</span>
                <span v-else class="price">¥{{ selectedGame.price }}</span>
              </div>
            </div>
            <div class="modal-actions">
              <button 
                class="btn btn-primary btn-large"
                @click="addToCart(selectedGame)"
                :disabled="selectedGame.inCart"
              >
                {{ selectedGame.inCart ? '已在购物车' : '加入购物车' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// 游戏接口定义
interface Game {
  id: number
  title: string
  description: string
  releaseDate: string
  price: number
  developer: string
  publisher: string
  coverImage: string
  inCart: boolean
  inWishlist: boolean
}

// 响应式数据
const games = ref<Game[]>([])
const searchQuery = ref('')
const sortBy = ref('title')
const priceFilter = ref('all')
const selectedGame = ref<Game | null>(null)
const hasMoreGames = ref(true)

// 发送事件给父组件
const emit = defineEmits<{
  addToCart: [game: Game]
  addToWishlist: [game: Game]
}>()

// 计算属性 - 过滤和排序游戏
const filteredGames = computed(() => {
  let filtered = games.value

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(game => 
      game.title.toLowerCase().includes(query) ||
      game.description.toLowerCase().includes(query) ||
      game.developer.toLowerCase().includes(query) ||
      game.publisher.toLowerCase().includes(query)
    )
  }

  // 价格过滤
  if (priceFilter.value !== 'all') {
    switch (priceFilter.value) {
      case 'free':
        filtered = filtered.filter(game => game.price === 0)
        break
      case 'under50':
        filtered = filtered.filter(game => game.price <= 50)
        break
      case 'under100':
        filtered = filtered.filter(game => game.price <= 100)
        break
    }
  }

  // 排序
  switch (sortBy.value) {
    case 'price':
      filtered.sort((a, b) => a.price - b.price)
      break
    case 'releaseDate':
      filtered.sort((a, b) => new Date(b.releaseDate).getTime() - new Date(a.releaseDate).getTime())
      break
    default:
      filtered.sort((a, b) => a.title.localeCompare(b.title))
  }

  return filtered
})

// 方法
const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const addToCart = (game: Game) => {
  game.inCart = true
  emit('addToCart', game)
}

const addToWishlist = (game: Game) => {
  game.inWishlist = !game.inWishlist
  emit('addToWishlist', game)
}

const viewGameDetails = (game: Game) => {
  selectedGame.value = game
}

const closeGameDetails = () => {
  selectedGame.value = null
}

const loadMoreGames = () => {
  // TODO: 实际项目中这里会调用API加载更多数据
  console.log('加载更多游戏...')
}

// 模拟游戏数据
const initMockData = () => {
  games.value = [
    {
      id: 1,
      title: "赛博朋克2077",
      description: "赛博朋克2077是一款开放世界角色扮演游戏，故事发生在夜之城，一个权力、魅力和身体改造痴迷的大都市。你扮演V，一个雇佣兵追求独一无二的植入物，这是获得永生的关键。",
      releaseDate: "2020-12-10",
      price: 298,
      developer: "CD Projekt RED",
      publisher: "CD Projekt",
      coverImage: "https://cdn.akamai.steamstatic.com/steam/apps/1091500/header.jpg",
      inCart: false,
      inWishlist: false
    },
    {
      id: 2,
      title: "艾尔登法环",
      description: "《艾尔登法环》是由FromSoftware开发并由万代南梦宫娱乐发行的动作角色扮演游戏。这是一个全新的奇幻世界，由宫崎英高和乔治·R·R·马丁共同创造。",
      releaseDate: "2022-02-25",
      price: 298,
      developer: "FromSoftware",
      publisher: "Bandai Namco Entertainment",
      coverImage: "https://cdn.akamai.steamstatic.com/steam/apps/1245620/header.jpg",
      inCart: false,
      inWishlist: false
    },
    {
      id: 3,
      title: "只狼：影逝二度",
      description: "在《只狼：影逝二度》中，你将扮演「狼」，一名身负耻辱的独臂武士，从敌人手中救出你的主君，一名拥有珍贵血统的年轻皇子，并向你的敌人复仇。",
      releaseDate: "2019-03-22",
      price: 268,
      developer: "FromSoftware",
      publisher: "Activision",
      coverImage: "https://cdn.akamai.steamstatic.com/steam/apps/814380/header.jpg",
      inCart: false,
      inWishlist: false
    },
    {
      id: 4,
      title: "Among Us",
      description: "《Among Us》是一款多人社交推理游戏，玩家需要在太空船上完成任务，同时找出隐藏在队伍中的冒名顶替者。团队合作和欺骗并存的游戏体验。",
      releaseDate: "2018-06-15",
      price: 12,
      developer: "InnerSloth",
      publisher: "InnerSloth",
      coverImage: "https://cdn.akamai.steamstatic.com/steam/apps/945360/header.jpg",
      inCart: false,
      inWishlist: false
    },
    {
      id: 5,
      title: "黑神话：悟空",
      description: "《黑神话：悟空》是由游戏科学制作的单机动作角色扮演游戏，以中国古典小说《西游记》为背景，让玩家扮演命运未卜的天命人，为寻求昔日的真相，踏上充满危险与惊奇的西游之路。",
      releaseDate: "2024-08-20",
      price: 268,
      developer: "游戏科学",
      publisher: "游戏科学",
      coverImage: "https://cdn.akamai.steamstatic.com/steam/apps/2358720/header.jpg",
      inCart: false,
      inWishlist: false
    }
  ]
}

// 组件挂载时初始化数据
onMounted(() => {
  initMockData()
})
</script>

<style scoped>
.game-store {
  width: 100%;
  height: 100%;
}

.store-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.search-section {
  display: flex;
  align-items: center;
  flex: 1;
  max-width: 400px;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px 0 0 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1.4rem; /* 增大字体 */
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.search-input:focus {
  outline: none;
  border-color: #a8edea;
}

.search-btn {
  padding: 0.75rem 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-left: none;
  border-radius: 0 8px 8px 0;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  cursor: pointer;
  font-size: 1.4rem; /* 增大字体 */
}

.filter-section {
  display: flex;
  gap: 1rem;
}

.filter-select {
  padding: 0.75rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1.4rem; /* 增大字体 */
}

.filter-select option {
  background: #2a5298;
  color: white;
}

.games-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.game-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.game-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  border-color: #a8edea;
}

.game-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.game-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.price-tag {
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: bold;
}

.free-price {
  color: white;
  font-weight: bold;
  font-size: 1.9rem;
}

.price {
  color: #a8edea;
  font-weight: bold;
  font-size: 2.0rem;
}

.game-info {
  padding: 1.5rem;
}

.game-title {
  font-size: 1.8rem; /* 增大字体 */
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: #a8edea;
}

.game-description {
  font-size: 1.3rem; /* 增大字体 */
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.4;
  margin-bottom: 1rem;
}

.game-details {
  margin-bottom: 1.5rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 1.4rem; /* 增大字体 */
}

.label {
  color: rgba(255, 255, 255, 0.7);
}

.value {
  color: white;
  font-weight: 500;
}

.game-actions {
  display: flex;
  gap: 0.75rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1.5rem; /* 增大字体 */
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(45deg, #a8edea, #fed6e3);
  color: #2c3e50;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(168, 237, 234, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  max-width: 60px;
  flex: none;
  text-indent: -9px;
  font-size: 1.4rem; /* 增大字体 */
}

.btn-outline {
  background: transparent;
  border: 2px solid rgba(255, 255, 255, 0.5);
  color: white;
  font-size: 1.3rem; /* 增大字体 */
}

.btn-outline:hover {
  border-color: white;
  background: rgba(255, 255, 255, 0.1);
}

.load-more {
  text-align: center;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.game-detail-modal {
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  border-radius: 20px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 2rem; /* 增大字体 */
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  z-index: 1001;
}

.modal-content {
  display: flex;
  flex-direction: column;
}

.modal-image {
  height: 300px;
  overflow: hidden;
  border-radius: 20px 20px 0 0;
}

.modal-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.modal-info {
  padding: 2rem;
}

.modal-info h2 {
  color: #a8edea;
  margin-bottom: 1rem;
  font-size: 3rem; /* 增大字体 */
}

.full-description {
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  margin-bottom: 2rem;
  font-size: 1.5rem; /* 增大字体 */
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
}

.detail-item {
  color: white;
  font-size: 2rem; /* 增大字体 */
}

.detail-item strong {
  color: #a8edea;
}

.modal-actions {
  text-align: center;
}

.btn-large {
  padding: 1rem 2rem;
  font-size: 2rem; /* 增大字体 */
}

@media (max-width: 768px) {
  .games-grid {
    grid-template-columns: 1fr;
  }
  
  .store-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-section {
    max-width: none;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
}

</style>