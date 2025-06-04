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
}

// 定义购物车中的游戏项
export interface CartItem {
  game: Game
  quantity: number
}

export const useGameStore = defineStore('game', () => {
  const userStore = useUserStore()
  const apiBaseUrl = 'http://localhost:5000/api'
  
  // 游戏列表数据
  const games = ref<Game[]>([])
  
  // 加载游戏列表
  async function loadGames() {
    try {
      const config = userStore.currentUser?.token ? {
        headers: {
          'Authorization': `Bearer ${userStore.currentUser.token}`
        }
      } : {}
      
      const response = await axios.get(`${apiBaseUrl}/games`, config)
      games.value = response.data.map((game: any) => ({
        id: game.id,
        title: game.title,
        description: game.description,
        type: game.type,
        releaseDate: game.release_date || '',  // 使用后端返回的格式化日期
        price: game.price,
        developer: game.developer,
        publisher: game.publisher,
        imageUrl: game.image_url
      }))
    } catch (error) {
      console.error('加载游戏列表失败', error)
    }
  }

  // 购物车数据
  const cartItems = ref<CartItem[]>([])
  
  // 游戏库数据
  const libraryGames = ref<Game[]>([])

  // 计算购物车中的总价
  const cartTotal = computed(() => {
    return cartItems.value.reduce((total, item) => {
      return total + (item.game.price * item.quantity)
    }, 0)
  })

  // 计算购物车中的游戏数量
  const cartCount = computed(() => {
    return cartItems.value.reduce((count, item) => count + item.quantity, 0)
  })

  // 从服务器加载用户的购物车
  async function loadUserCart() {
    if (!userStore.isLoggedIn) return
    
    try {
      const response = await axios.get(`${apiBaseUrl}/cart`)
      cartItems.value = response.data.items || []
    } catch (error) {
      console.error('加载购物车失败', error)
    }
  }
  
  // 从服务器加载用户的游戏库
  async function loadUserLibrary() {
    if (!userStore.isLoggedIn) return
    
    try {
      const response = await axios.get(`${apiBaseUrl}/library`)
      libraryGames.value = response.data.games || []
    } catch (error) {
      console.error('加载游戏库失败', error)
    }
  }

  // 添加游戏到购物车
  async function addToCart(game: Game) {
    const existingItem = cartItems.value.find(item => item.game.id === game.id)
    
    if (existingItem) {
      existingItem.quantity++
    } else {
      cartItems.value.push({
        game,
        quantity: 1
      })
    }
    
    // 如果用户已登录，同步到服务器
    if (userStore.isLoggedIn) {
      try {
        await axios.post(`${apiBaseUrl}/cart/add`, { gameId: game.id, quantity: 1 })
      } catch (error) {
        console.error('添加到购物车失败', error)
      }
    }
  }

  // 从购物车移除游戏
  async function removeFromCart(gameId: number) {
    const index = cartItems.value.findIndex(item => item.game.id === gameId)
    if (index !== -1) {
      cartItems.value.splice(index, 1)
      
      // 如果用户已登录，同步到服务器
      if (userStore.isLoggedIn) {
        try {
          await axios.delete(`${apiBaseUrl}/cart/remove/${gameId}`)
        } catch (error) {
          console.error('从购物车移除失败', error)
        }
      }
    }
  }

  // 更新购物车中游戏的数量
  async function updateCartItemQuantity(gameId: number, quantity: number) {
    const item = cartItems.value.find(item => item.game.id === gameId)
    if (item) {
      item.quantity = quantity
      // 如果数量为0，从购物车中移除
      if (quantity <= 0) {
        removeFromCart(gameId)
        return
      }
      
      // 如果用户已登录，同步到服务器
      if (userStore.isLoggedIn) {
        try {
          await axios.put(`${apiBaseUrl}/cart/update`, { gameId, quantity })
        } catch (error) {
          console.error('更新购物车数量失败', error)
        }
      }
    }
  }

  // 购买购物车中的所有游戏
  async function purchaseGames() {
    // 如果用户已登录，通过API购买
    if (userStore.isLoggedIn) {
      try {
        const response = await axios.post(`${apiBaseUrl}/purchase`)
        libraryGames.value = [...libraryGames.value, ...response.data.purchasedGames]
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
    updateCartItemQuantity,
    purchaseGames,
    isInLibrary,
    isInCart
  }
})