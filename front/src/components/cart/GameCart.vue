<template>
  <div class="cart-container">
    <!-- 购物车标题 -->
    <div class="cart-header">
      <h2>购物车</h2>
      <span class="cart-count">{{ cartItems.length }} 个商品</span>
    </div>

    <!-- 购物车为空时的显示 -->
    <div v-if="cartItems.length === 0" class="empty-cart">
      <div class="empty-icon">🛒</div>
      <h3>购物车是空的</h3>
      <p>快去添加一些心仪的游戏吧！</p>
    </div>

    <!-- 购物车商品列表 -->
    <div v-else class="cart-content">
      <div class="cart-items">
        <div 
          v-for="item in cartItems" 
          :key="item.id"
          class="cart-item"
        >
          <!-- 游戏封面 -->
          <div class="item-image">
            <img :src="item.coverImage" :alt="item.title" />
          </div>

          <!-- 游戏信息 -->
          <div class="item-info">
            <h3 class="item-title">{{ item.title }}</h3>
            <p class="item-description">{{ truncateText(item.description, 80) }}</p>
            <div class="item-details">
              <span class="developer">{{ item.developer }}</span>
              <span class="release-date">{{ formatDate(item.releaseDate) }}</span>
            </div>
          </div>

          <!-- 价格和操作 -->
          <div class="item-actions">
            <div class="price-section">
              <span v-if="item.price === 0" class="free-price">免费</span>
              <span v-else class="price">¥{{ item.price }}</span>
            </div>
            <div class="action-buttons">
              <button 
                class="btn btn-secondary"
                @click="moveToWishlist(item)"
                title="移至愿望单"
              >
                🤍
              </button>
              <button 
                class="btn btn-danger"
                @click="removeFromCart(item)"
                title="从购物车移除"
              >
                🗑️
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 购物车汇总 -->
      <div class="cart-summary">
        <div class="summary-content">
          <div class="summary-header">
            <h3>订单汇总</h3>
          </div>
          
          <div class="summary-details">
            <div class="summary-row">
              <span>商品数量:</span>
              <span>{{ cartItems.length }} 个</span>
            </div>
            <div class="summary-row">
              <span>免费游戏:</span>
              <span>{{ freeGamesCount }} 个</span>
            </div>
            <div class="summary-row">
              <span>付费游戏:</span>
              <span>{{ paidGamesCount }} 个</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-row total-row">
              <span>总计:</span>
              <span class="total-price">¥{{ totalPrice }}</span>
            </div>
          </div>

          <div class="checkout-section">
            <button 
              class="btn btn-primary btn-large checkout-btn"
              @click="handleCheckout"
              :disabled="isProcessing"
            >
              {{ isProcessing ? '处理中...' : '结算购买' }}
            </button>
            <button 
              class="btn btn-outline clear-btn"
              @click="clearCart"
            >
              清空购物车
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 结算确认弹窗 -->
    <div class="modal-overlay" v-if="showCheckoutModal" @click="closeCheckoutModal">
      <div class="checkout-modal" @click.stop>
        <h3>确认购买</h3>
        <div class="checkout-summary">
          <p>您即将购买以下游戏：</p>
          <div class="checkout-items">
            <div v-for="item in cartItems" :key="item.id" class="checkout-item">
              <span class="checkout-title">{{ item.title }}</span>
              <span class="checkout-price">
                {{ item.price === 0 ? '免费' : '¥' + item.price }}
              </span>
            </div>
          </div>
          <div class="checkout-total">
            <strong>总计: ¥{{ totalPrice }}</strong>
          </div>
        </div>
        <div class="modal-buttons">
          <button class="btn btn-outline" @click="closeCheckoutModal">取消</button>
          <button class="btn btn-primary" @click="confirmPurchase">确认购买</button>
        </div>
      </div>
    </div>

    <!-- 成功购买弹窗 -->
    <div class="modal-overlay" v-if="showSuccessModal" @click="closeSuccessModal">
      <div class="success-modal" @click.stop>
        <div class="success-icon">✅</div>
        <h3>购买成功！</h3>
        <p>游戏已添加到您的游戏库中</p>
        <div class="purchased-games">
          <div v-for="game in purchasedGames" :key="game.id" class="purchased-item">
            {{ game.title }}
          </div>
        </div>
        <button class="btn btn-primary" @click="closeSuccessModal">
          确定
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

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

// Props
interface Props {
  cartItems: Game[]
}

const props = withDefaults(defineProps<Props>(), {
  cartItems: () => []
})

// 发送事件给父组件
const emit = defineEmits<{
  removeFromCart: [game: Game]
  moveToWishlist: [game: Game]
  clearCart: []
  purchaseGames: [games: Game[]]
  updateCartCount: [count: number]
}>()

// 响应式数据
const isProcessing = ref(false)
const showCheckoutModal = ref(false)
const showSuccessModal = ref(false)
const purchasedGames = ref<Game[]>([])

// 计算属性
const totalPrice = computed(() => {
  return props.cartItems.reduce((total, item) => total + item.price, 0)
})

const freeGamesCount = computed(() => {
  return props.cartItems.filter(item => item.price === 0).length
})

const paidGamesCount = computed(() => {
  return props.cartItems.filter(item => item.price > 0).length
})

// 监听购物车变化，更新父组件的计数
watch(() => props.cartItems.length, (newCount) => {
  emit('updateCartCount', newCount)
}, { immediate: true })

// 方法
const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const removeFromCart = (game: Game) => {
  emit('removeFromCart', game)
}

const moveToWishlist = (game: Game) => {
  // 先从购物车移除，再添加到愿望单
  emit('removeFromCart', game)
  emit('moveToWishlist', game)
}

const clearCart = () => {
  if (confirm('确定要清空购物车吗？')) {
    emit('clearCart')
  }
}

const handleCheckout = () => {
  if (props.cartItems.length === 0) return
  showCheckoutModal.value = true
}

const closeCheckoutModal = () => {
  showCheckoutModal.value = false
}

const confirmPurchase = async () => {
  isProcessing.value = true
  
  try {
    // 模拟购买处理时间
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 保存购买的游戏列表
    purchasedGames.value = [...props.cartItems]
    
    // 发送购买事件给父组件
    emit('purchaseGames', props.cartItems)
    
    // 关闭结算弹窗，显示成功弹窗
    showCheckoutModal.value = false
    showSuccessModal.value = true
    
  } catch (error) {
    console.error('购买失败:', error)
    alert('购买失败，请重试')
  } finally {
    isProcessing.value = false
  }
}

const closeSuccessModal = () => {
  showSuccessModal.value = false
  purchasedGames.value = []
}
</script>

<style scoped>
.cart-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

.cart-header h2 {
  color: #a8edea;
  margin: 0;
  font-size: 2.5rem;
}

.cart-count {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.6rem;
}

.empty-cart {
  text-align: center;
  padding: 4rem 2rem;
  color: rgba(255, 255, 255, 0.8);
}

.empty-icon {
  font-size: 6rem;
  margin-bottom: 1rem;
}

.empty-cart h3 {
  font-size: 2.2rem;
  margin-bottom: 1rem;
  color: #a8edea;
}

.empty-cart p {
  font-size: 1.6rem;
}

.cart-content {
  display: flex;
  gap: 2rem;
  flex: 1;
}

.cart-items {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.cart-item {
  display: flex;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.cart-item:hover {
  border-color: #a8edea;
  transform: translateY(-2px);
}

.item-image {
  width: 120px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-info {
  flex: 1;
  padding-left: 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.item-title {
  color: #a8edea;
  margin: 0 0 0.5rem 0;
  font-size: 1.8rem;
  font-weight: bold;
}

.item-description {
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 0.5rem 0;
  font-size: 1.4rem;
  line-height: 1.4;
}

.item-details {
  display: flex;
  gap: 1rem;
  font-size: 1.3rem;
  color: rgba(255, 255, 255, 0.6);
}

.item-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-between;
  padding-left: 1rem;
}

.price-section {
  margin-bottom: 1rem;
}

.free-price {
  color: #4CAF50;
  font-weight: bold;
  font-size: 1.8rem;
}

.price {
  color: #a8edea;
  font-weight: bold;
  font-size: 2rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.cart-summary {
  flex: 1;
  max-width: 350px;
}

.summary-content {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: sticky;
  top: 2rem;
}

.summary-header h3 {
  color: #a8edea;
  margin: 0 0 1.5rem 0;
  font-size: 2rem;
  text-align: center;
}

.summary-details {
  margin-bottom: 2rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.8rem;
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.9);
}

.summary-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.3);
  margin: 1rem 0;
}

.total-row {
  font-size: 1.8rem;
  font-weight: bold;
  color: #a8edea;
}

.total-price {
  color: #a8edea;
  font-size: 2rem;
}

.checkout-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
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
  font-size: 1.4rem;
  min-width: 40px;
}

.btn-danger {
  background: rgba(255, 71, 87, 0.8);
  color: white;
  font-size: 1.4rem;
  min-width: 40px;
}

.btn-danger:hover {
  background: rgba(255, 71, 87, 1);
}

.btn-outline {
  background: transparent;
  border: 2px solid rgba(255, 255, 255, 0.5);
  color: white;
}

.btn-outline:hover {
  border-color: white;
  background: rgba(255, 255, 255, 0.1);
}

.btn-large {
  padding: 1rem 2rem;
  font-size: 1.8rem;
}

.checkout-btn {
  margin-bottom: 0.5rem;
}

.clear-btn {
  font-size: 1.4rem;
}

/* 弹窗样式 */
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
}

.checkout-modal,
.success-modal {
  background: white;
  padding: 2rem;
  border-radius: 15px;
  width: 100%;
  max-width: 500px;
  color: #2c3e50;
}

.checkout-modal h3,
.success-modal h3 {
  margin-top: 0;
  text-align: center;
  color: #2c3e50;
  font-size: 2rem;
}

.checkout-summary {
  margin: 1.5rem 0;
}

.checkout-items {
  margin: 1rem 0;
  max-height: 200px;
  overflow-y: auto;
}

.checkout-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
  font-size: 1.4rem;
}

.checkout-total {
  text-align: right;
  margin-top: 1rem;
  font-size: 1.8rem;
  color: #2c3e50;
}

.modal-buttons {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.success-icon {
  text-align: center;
  font-size: 4rem;
  margin-bottom: 1rem;
}

.purchased-games {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
  max-height: 150px;
  overflow-y: auto;
}

.purchased-item {
  padding: 0.5rem 0;
  border-bottom: 1px solid #dee2e6;
  font-size: 1.4rem;
}

.purchased-item:last-child {
  border-bottom: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .cart-content {
    flex-direction: column;
  }
  
  .cart-summary {
    max-width: none;
  }
  
  .cart-item {
    flex-direction: column;
    gap: 1rem;
  }
  
  .item-image {
    width: 100%;
    height: 150px;
  }
  
  .item-info {
    padding-left: 0;
  }
  
  .item-actions {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding-left: 0;
  }
  
  .action-buttons {
    order: 2;
  }
  
  .price-section {
    order: 1;
    margin-bottom: 0;
  }
}
</style>