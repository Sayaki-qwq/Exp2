<template>
  <div class="admin-container">
    <h1>游戏管理</h1>
    
    <!-- 添加游戏按钮 -->
    <button class="btn-add" @click="showAddForm = true">添加新游戏</button>
    
    <!-- 游戏列表 -->
    <div class="games-list">
      <div v-for="game in gameStore.games" :key="game.id" class="game-item">
        <div class="game-info">
          <img :src="game.imageUrl" :alt="game.title" class="game-image">
          <div class="game-details">
            <h3>{{ game.title }}</h3>
            <p class="type">类型：{{ game.type }}</p>
            <p class="release-date">发行日期：{{ game.releaseDate || '暂无' }}</p>
            <p class="price">价格：¥{{ formatPrice(game.price) }}</p>
            <p class="developer">开发商：{{ game.developer }}</p>
            <p class="publisher">发行商：{{ game.publisher }}</p>
          </div>
        </div>
        <div class="game-actions">
          <button class="btn-edit" @click="editGame(game)">编辑</button>
          <button class="btn-delete" @click="confirmDelete(game)">删除</button>
        </div>
      </div>
    </div>
    
    <!-- 添加/编辑游戏的弹窗 -->
    <div v-if="showAddForm || editingGame" class="modal">
      <div class="modal-content">
        <h2>{{ editingGame ? '编辑游戏' : '添加新游戏' }}</h2>
        <form @submit.prevent="submitForm">
          <div class="form-group">
            <label for="title">游戏标题</label>
            <input 
              id="title" 
              v-model="gameForm.title" 
              required
              placeholder="请输入游戏标题"
            >
          </div>
          
          <div class="form-group">
            <label for="description">游戏描述</label>
            <textarea 
              id="description" 
              v-model="gameForm.description" 
              required
              placeholder="请输入游戏描述"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label for="type">游戏类型</label>
            <input 
              id="type" 
              v-model="gameForm.type" 
              required
              placeholder="例如：RPG、动作、策略等"
            >
          </div>
          
          <div class="form-group">
            <label for="release_date">发行日期</label>
            <input 
              id="release_date" 
              type="date" 
              v-model="gameForm.release_date" 
              required
            >
          </div>
          
          <div class="form-group">
            <label for="price">价格</label>
            <input 
              id="price" 
              type="number" 
              v-model="gameForm.price" 
              required
              min="0"
              step="0.01"
            >
          </div>
          
          <div class="form-group">
            <label for="developer">开发商</label>
            <input 
              id="developer" 
              v-model="gameForm.developer" 
              required
              placeholder="请输入开发商名称"
            >
          </div>
          
          <div class="form-group">
            <label for="publisher">发行商</label>
            <input 
              id="publisher" 
              v-model="gameForm.publisher" 
              required
              placeholder="请输入发行商名称"
            >
          </div>
          
          <div class="form-group">
            <label for="imageUrl">游戏图片URL</label>
            <input 
              id="imageUrl" 
              v-model="gameForm.imageUrl" 
              required
              placeholder="请输入游戏图片的URL地址"
            >
          </div>
          
          <div class="form-actions">
            <button type="submit" class="btn-submit">
              {{ editingGame ? '保存修改' : '添加游戏' }}
            </button>
            <button type="button" class="btn-cancel" @click="closeForm">取消</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteConfirm" class="modal">
      <div class="modal-content delete-confirm">
        <h2>确认删除</h2>
        <p>确定要删除游戏"{{ gameToDelete?.title }}"吗？此操作不可撤销。</p>
        <div class="form-actions">
          <button class="btn-delete" @click="deleteGame">确认删除</button>
          <button class="btn-cancel" @click="showDeleteConfirm = false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive } from 'vue'
import { useGameStore } from '@/stores/gameStore'
import { useUserStore } from '@/stores/userStore'
import { formatPrice } from '@/utils/formatters'
import axios from 'axios'

export default defineComponent({
  name: 'AdminView',
  setup() {
    const gameStore = useGameStore()
    const userStore = useUserStore()
    const showAddForm = ref(false)
    const showDeleteConfirm = ref(false)
    const editingGame = ref<any>(null)
    const gameToDelete = ref<any>(null)
    
    const gameForm = reactive({
      title: '',
      description: '',
      type: '',
      release_date: '',
      price: 0,
      developer: '',
      publisher: '',
      imageUrl: ''
    })
    
    // 添加 axios 请求配置
    const getAxiosConfig = () => ({
      headers: {
        'Authorization': `Bearer ${userStore.currentUser?.token}`
      }
    })
    
    // 初始化表单数据
    const initForm = (game?: any) => {
      if (game) {
        gameForm.title = game.title
        gameForm.description = game.description
        gameForm.type = game.type
        gameForm.release_date = game.releaseDate || ''
        gameForm.price = game.price
        gameForm.developer = game.developer
        gameForm.publisher = game.publisher
        gameForm.imageUrl = game.imageUrl
      } else {
        gameForm.title = ''
        gameForm.description = ''
        gameForm.type = ''
        gameForm.release_date = ''
        gameForm.price = 0
        gameForm.developer = ''
        gameForm.publisher = ''
        gameForm.imageUrl = ''
      }
    }
    
    // 编辑游戏
    const editGame = (game: any) => {
      editingGame.value = game
      initForm(game)
      showAddForm.value = true
    }
    
    // 确认删除
    const confirmDelete = (game: any) => {
      gameToDelete.value = game
      showDeleteConfirm.value = true
    }
    
    // 删除游戏
    const deleteGame = async () => {
      try {
        await axios.delete(
          `http://localhost:5000/api/games/${gameToDelete.value.id}`,
          getAxiosConfig()
        )
        await gameStore.loadGames()
        showDeleteConfirm.value = false
        gameToDelete.value = null
      } catch (error: any) {
        alert(error.response?.data?.message || '删除失败')
      }
    }
    
    // 提交表单
    const submitForm = async () => {
      try {
        const formData = { ...gameForm }
        // 确保日期格式正确
        if (formData.release_date) {
          formData.release_date = formData.release_date.split('T')[0]
        }
        
        // 将前端的字段名转换为后端期望的格式
        const backendData = {
          title: formData.title,
          description: formData.description,
          type: formData.type,
          release_date: formData.release_date,
          price: formData.price,
          developer: formData.developer,
          publisher: formData.publisher,
          image_url: formData.imageUrl  // 将 imageUrl 转换为 image_url
        }
        
        if (editingGame.value) {
          // 更新游戏
          await axios.put(
            `http://localhost:5000/api/games/${editingGame.value.id}`,
            backendData,
            getAxiosConfig()
          )
        } else {
          // 添加新游戏
          await axios.post(
            'http://localhost:5000/api/games',
            backendData,
            getAxiosConfig()
          )
        }
        await gameStore.loadGames()
        closeForm()
      } catch (error: any) {
        alert(error.response?.data?.message || '操作失败')
      }
    }
    
    // 关闭表单
    const closeForm = () => {
      showAddForm.value = false
      editingGame.value = null
      initForm()
    }
    
    return {
      gameStore,
      userStore,
      showAddForm,
      showDeleteConfirm,
      editingGame,
      gameToDelete,
      gameForm,
      editGame,
      confirmDelete,
      deleteGame,
      submitForm,
      closeForm,
      formatPrice
    }
  }
})
</script>

<style scoped>
.admin-container {
  padding: 2rem;
  max-width: 1600px;
  margin: 0 auto;
}

h1 {
  font-size: 2.5rem;
  color: #ffffff;
  margin-bottom: 1.5rem;
  text-align: center;
}

.btn-add {
  background-color: #5c7e10;
  color: white;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 2rem;
  font-size: 1.1rem;
  transition: background-color 0.3s;
}

.btn-add:hover {
  background-color: #6d9619;
}

.games-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 1.5rem;
}

.game-item {
  background-color: #2a475e;
  border-radius: 8px;
  padding: 1.2rem;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  gap: 1.5rem;
}

.game-info {
  display: flex;
  flex-direction: row;
  gap: 1.5rem;
  flex: 1;
  font-size: 1.2rem;
}

.game-image {
  width: 160px;
  height: 90px;
  object-fit: cover;
  border-radius: 6px;
  flex-shrink: 0;
}

.game-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.game-details h3 {
  margin: 0 0 0.5rem 0;
  color: #ffffff;
  font-size: 1.4rem;
  line-height: 1.2;
}

.game-details p {
  margin: 0.2rem 0;
  color: #c7d5e0;
  font-size: 1rem;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.game-actions {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  width: 120px;
  flex-shrink: 0;
}

.btn-edit {
  background-color: #387198;
  color: white;
  border: none;
  padding: 0.6rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  flex: 1;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.btn-edit:hover {
  background-color: #4a8db8;
}

.btn-delete {
  background-color: #c23b22;
  color: white;
  border: none;
  padding: 0.6rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  flex: 1;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.btn-delete:hover {
  background-color: #d44332;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #1b2838;
  padding: 2.5rem;
  border-radius: 12px;
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h2 {
  font-size: 1.8rem;
  color: #ffffff;
  margin-bottom: 1.5rem;
  text-align: center;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.8rem;
  color: #c7d5e0;
  font-size: 1.1rem;
  font-weight: 500;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #4b5f74;
  border-radius: 6px;
  background-color: #2a475e;
  color: #c7d5e0;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #5c7e10;
  outline: none;
}

.form-group textarea {
  height: 120px;
  resize: vertical;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-submit {
  background-color: #5c7e10;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  flex: 1;
  font-size: 1.1rem;
  transition: background-color 0.3s;
}

.btn-submit:hover {
  background-color: #6d9619;
}

.btn-cancel {
  background-color: #8f98a0;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  flex: 1;
  font-size: 1.1rem;
  transition: background-color 0.3s;
}

.btn-cancel:hover {
  background-color: #a5b4bb;
}

.delete-confirm {
  text-align: center;
}

.delete-confirm p {
  margin: 1.5rem 0;
  color: #c7d5e0;
  font-size: 1.1rem;
}
</style> 