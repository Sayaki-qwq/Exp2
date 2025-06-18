import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import axios from 'axios'
import { useUserStore } from './userStore'

// 定义游戏类型接口
  export interface Game {
    id: number
    title: string
    description: string
    type: string
    releaseDate: string
    price: number
    developer: string
    publisher: string
    imageUrl: string
    likePercentage?: number
  }

// 定义购物车中的游戏项
export interface CartItem {
  game: Game
}

// 定义游戏评分接口
export interface GameRating {
  like_count: number
  dislike_count: number
  total_count: number
  like_percentage: number
}

// 定义用户评分接口
export interface UserRating {
  rating: 'like' | 'dislike' | null
  comment: string | null
}

// 定义游戏评论接口
export interface GameReview {
  id: number
  rating: 'like' | 'dislike'
  comment: string
  username: string
  created_at: string
  updated_at: string
}

export const useGameStore = defineStore('game', () => {
  const userStore = useUserStore()
  const apiBaseUrl = 'http://localhost:5000/api'
  
  // 游戏列表数据
  const games = ref<Game[]>([])
  
  // 搜索结果数据
  const searchResults = ref<Game[]>([])
  const isSearching = ref(false)
  const searchQuery = ref('')

  // 排序相关状态
  const sortBy = ref<'release_date' | 'price' | 'like_percentage' | 'default'>('default')
  const sortOrder = ref<'asc' | 'desc'>('desc') // 默认降序
  
  // 加载游戏列表
  async function loadGames() {
    try {
      const response = await axios.get(`${apiBaseUrl}/games`)
      games.value = response.data.map((game: any) => ({
        id: game.id,
        title: game.title,
        description: game.description,
        type: game.type,
        releaseDate: game.release_date || '',
        price: game.price,
        developer: game.developer,
        publisher: game.publisher,
        imageUrl: game.image_url,
        likePercentage: game.like_percentage || 0,
      }))
    } catch (error) {
      console.error('加载游戏列表失败', error)
    }
  }

  // 搜索游戏
  async function searchGames(query: string) {
    if (!query.trim()) {
      searchResults.value = []
      searchQuery.value = ''
      return
    }

    isSearching.value = true
    searchQuery.value = query
    
    try {
      const response = await axios.get(`${apiBaseUrl}/games/search`, {
        params: { q: query }
      })
      
      searchResults.value = (Array.isArray(response.data) ? response.data : []).map((game: any) => ({
        id: game.id,
        title: game.title,
        description: game.description,
        type: game.type,
        releaseDate: game.release_date || '',
        price: game.price,
        developer: game.developer,
        publisher: game.publisher,
        imageUrl: game.image_url,
        likePercentage: game.like_percentage || 0,
      }))
    } catch (error) {
      console.error('搜索游戏失败', error)
      searchResults.value = []
    } finally {
      isSearching.value = false
    }
  }

  // 清空搜索结果
  function clearSearch() {
    searchResults.value = []
    searchQuery.value = ''
    isSearching.value = false
  }

  // 获取当前显示的游戏列表（搜索结果或全部游戏）
  const displayGames = computed(() => {
    const baseGames = searchQuery.value ? searchResults.value : games.value
    
    if (sortBy.value === 'default') {
      return baseGames
    }
    
    return [...baseGames].sort((a, b) => {
      let aValue: any
      let bValue: any
      
      if (sortBy.value === 'release_date') {
        aValue = new Date(a.releaseDate)
        bValue = new Date(b.releaseDate)
      } else if (sortBy.value === 'price') {
        aValue = Number(a.price)
        bValue = Number(b.price)
      } else if (sortBy.value === 'like_percentage') {
        aValue = Number(a.likePercentage || 0)
        bValue = Number(b.likePercentage || 0)
      } else {
        return 0
      }
      
      if (sortOrder.value === 'asc') {
        return aValue > bValue ? 1 : aValue < bValue ? -1 : 0
      } else {
        return aValue < bValue ? 1 : aValue > bValue ? -1 : 0
      }
    })
  })

  // 购物车数据
  const cartItems = ref<CartItem[]>([])
  
  // 游戏库数据
  const libraryGames = ref<Game[]>([])

  // 计算购物车中的总价
  const cartTotal = computed(() => {
    return cartItems.value.reduce((total, item) => {
      return total + Number(item.game.price)
    }, 0)
  })

  // 计算购物车中的游戏数量
  const cartCount = computed(() => {
    return cartItems.value.length
  })

  // 从服务器加载用户的购物车
  async function loadUserCart() {
    if (!userStore.isLoggedIn) return
    
    try {
      const response = await axios.get(`${apiBaseUrl}/cart`)
      cartItems.value = response.data.items.map((item: any) => ({
        game: {
          id: item.id,
          title: item.title,
          description: item.description,
          type: item.type,
          releaseDate: item.release_date,
          price: item.price,
          developer: item.developer,
          publisher: item.publisher,
          imageUrl: item.image_url,
          likePercentage: item.like_percentage || 0,
        }
      }))
    } catch (error) {
      console.error('加载购物车失败', error)
    }
  }
  
  // 从服务器加载用户的游戏库
  async function loadUserLibrary() {
    if (!userStore.isLoggedIn) return
    
    try {
      const response = await axios.get(`${apiBaseUrl}/library`)
      libraryGames.value = (response.data.games || []).map((game: any) => ({
        id: game.id,
        title: game.title,
        description: game.description,
        type: game.type,
        releaseDate: game.release_date || '',
        price: game.price,
        developer: game.developer,
        publisher: game.publisher,
        imageUrl: game.image_url,
        likePercentage: game.like_percentage || 0,
      }))
    } catch (error) {
      console.error('加载游戏库失败', error)
    }
  }

  // 添加游戏到购物车
  async function addToCart(game: Game) {
    if (!userStore.isLoggedIn) {
      alert('请先登录')
      return false
    }

      try {
      await axios.post(`${apiBaseUrl}/cart/add`, { 
        gameId: game.id
      })
      
      // 重新加载购物车
      await loadUserCart()
      return true
      } catch (error) {
        console.error('添加到购物车失败', error)
      return false
    }
  }

  // 从购物车移除游戏
  async function removeFromCart(gameId: number) {
    if (!userStore.isLoggedIn) return
      
        try {
          await axios.delete(`${apiBaseUrl}/cart/remove/${gameId}`)
      // 重新加载购物车
      await loadUserCart()
        } catch (error) {
          console.error('从购物车移除失败', error)
    }
  }

  // 购买购物车中的所有游戏
  async function purchaseGames() {
    // 如果用户已登录，通过API购买
    if (userStore.isLoggedIn) {
      try {
        const response = await axios.post(`${apiBaseUrl}/purchase`)
        const purchasedGames = (response.data.purchasedGames || []).map((game: any) => ({
          id: game.id,
          title: game.title,
          description: game.description,
          type: game.type,
          releaseDate: game.release_date || '',
          price: game.price,
          developer: game.developer,
          publisher: game.publisher,
          imageUrl: game.image_url
        }))
        libraryGames.value = [...libraryGames.value, ...purchasedGames]
        cartItems.value = []
        return true
      } catch (error) {
        console.error('购买失败', error)
        return false
      }
    } else {
      // 本地模式：将购物车中的游戏添加到游戏库
      cartItems.value.forEach(item => {
        if (!libraryGames.value.some(game => game.id === item.game.id)) {
          libraryGames.value.push(item.game)
        }
      })
      
      // 清空购物车
      cartItems.value = []
      return true
    }
  }

  // 检查游戏是否已在游戏库中
  function isInLibrary(gameId: number) {
    return libraryGames.value.some(game => game.id === gameId)
  }

  // 检查游戏是否已在购物车中
  function isInCart(gameId: number) {
    return cartItems.value.some(item => item.game.id === gameId)
  }
  
  // 监听用户登录状态变化
  watch(
    () => userStore.isLoggedIn,
    (isLoggedIn) => {
      if (isLoggedIn) {
        // 用户登录后加载数据
        loadUserCart()
        loadUserLibrary()
      } else {
        // 用户登出后清空数据
        cartItems.value = []
        libraryGames.value = []
      }
    },
    { immediate: true }
  )

  // 设置排序方式
  function setSortBy(field: 'release_date' | 'price' | 'like_percentage' | 'default') {
    sortBy.value = field
  }
  
  // 设置排序顺序
  function setSortOrder(order: 'asc' | 'desc') {
    sortOrder.value = order
  }

  // 评分相关功能
  
  // 获取游戏评分统计
  async function getGameRatings(gameId: number): Promise<GameRating | null> {
    try {
      const response = await axios.get(`${apiBaseUrl}/games/${gameId}/ratings`)
      return response.data
    } catch (error) {
      console.error('获取游戏评分失败', error)
      return null
    }
  }

  // 获取用户对游戏的评分
  async function getUserRating(gameId: number): Promise<UserRating | null> {
    if (!userStore.isLoggedIn) return null
    
    try {
      const response = await axios.get(`${apiBaseUrl}/games/${gameId}/ratings/user`)
      return response.data
    } catch (error) {
      console.error('获取用户评分失败', error)
      return null
    }
  }

  // 用户对游戏进行评分
  async function rateGame(gameId: number, rating: 'like' | 'dislike'): Promise<boolean> {
    if (!userStore.isLoggedIn) {
      alert('请先登录')
      return false
    }

    try {
      await axios.post(`${apiBaseUrl}/games/${gameId}/ratings`, { rating })
      return true
    } catch (error) {
      console.error('评分失败', error)
      return false
    }
  }

  // 删除用户对游戏的评分
  async function deleteRating(gameId: number): Promise<boolean> {
    if (!userStore.isLoggedIn) return false

    try {
      await axios.delete(`${apiBaseUrl}/games/${gameId}/ratings`)
      return true
    } catch (error) {
      console.error('删除评分失败', error)
      return false
    }
  }

  // 获取游戏的所有评论
  async function getGameReviews(gameId: number): Promise<GameReview[]> {
    try {
      const response = await axios.get(`${apiBaseUrl}/games/${gameId}/reviews`)
      return response.data
    } catch (error) {
      console.error('获取游戏评论失败', error)
      return []
    }
  }

  // 发表评论
  async function addReview(gameId: number, rating: 'like' | 'dislike', comment: string): Promise<boolean> {
    if (!userStore.isLoggedIn) {
      alert('请先登录')
      return false
    }

    try {
      await axios.post(`${apiBaseUrl}/games/${gameId}/reviews`, { rating, comment })
      return true
    } catch (error: any) {
      console.error('发表评论失败', error)
      const message = error.response?.data?.message || '发表评论失败'
      alert(message)
      return false
    }
  }

  // 删除评论
  async function deleteReview(gameId: number): Promise<boolean> {
    if (!userStore.isLoggedIn) return false

    try {
      await axios.delete(`${apiBaseUrl}/games/${gameId}/reviews`)
      return true
    } catch (error) {
      console.error('删除评论失败', error)
      return false
    }
  }

  return {
    games,
    cartItems,
    libraryGames,
    cartTotal,
    cartCount,
    loadGames,
    loadUserCart,
    loadUserLibrary,
    addToCart,
    removeFromCart,
    purchaseGames,
    isInLibrary,
    isInCart,
    searchGames,
    clearSearch,
    searchResults,
    isSearching,
    searchQuery,
    displayGames,
    sortBy,
    sortOrder,
    setSortBy,
    setSortOrder,
    // 评分功能
    getGameRatings,
    getUserRating,
    rateGame,
    deleteRating,
    // 评论功能
    getGameReviews,
    addReview,
    deleteReview
  }
})