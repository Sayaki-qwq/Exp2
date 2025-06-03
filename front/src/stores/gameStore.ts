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
  const games = ref<Game[]>([
    {
      id: 1,
      title: '赛博朋克2077',
      description: '一款开放世界动作冒险RPG游戏，故事发生在夜之城，一个由权力、魅力和身体改造痴迷的人所统治的巨型都市。',
      type: 'RPG',
      releaseDate: '2020-12-10',
      price: 298,
      developer: 'CD Projekt Red',
      publisher: 'CD Projekt',
      imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/1091500/header.jpg'
    },
    {
      id: 2,
      title: '艾尔登法环',
      description: '一款由FromSoftware开发的动作角色扮演游戏，由《黑暗之魂》系列的宫崎英高和奇幻作家乔治·R·R·马丁共同创作。',
      type: '动作角色扮演',
      releaseDate: '2022-02-25',
      price: 298,
      developer: 'FromSoftware',
      publisher: 'Bandai Namco Entertainment',
      imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/1245620/header.jpg'
    },
    {
      id: 3,
      title: '荒野大镖客：救赎2',
      description: '一款由Rockstar Games开发的西部题材动作冒险游戏，是2010年《荒野大镖客：救赎》的前传。',
      type: '动作冒险',
      releaseDate: '2018-10-26',
      price: 249,
      developer: 'Rockstar Games',
      publisher: 'Rockstar Games',
      imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/1174180/header.jpg'
    },
    {
      id: 4,
      title: '巫师3：狂猎',
      description: '一款由CD Projekt RED开发的动作角色扮演游戏，基于安杰伊·萨普科夫斯基的奇幻小说系列《巫师》改编。',
      type: 'RPG',
      releaseDate: '2015-05-19',
      price: 127,
      developer: 'CD Projekt Red',
      publisher: 'CD Projekt',
      imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/292030/header.jpg'
    },
    {
      id: 5,
      title: '半条命：Alyx',
      description: 'Valve开发的VR第一人称射击游戏，是《半条命》系列的最新作品。',
      type: 'VR射击',
      releaseDate: '2020-03-23',
      price: 149,
      developer: 'Valve',
      publisher: 'Valve',
      imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/546560/header.jpg'
    }
  ])

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