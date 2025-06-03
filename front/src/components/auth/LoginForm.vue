<template>
  <div class="login-form">
    <h2>用户登录</h2>
    
    <div v-if="userStore.error" class="error-message">
      {{ userStore.error }}
    </div>
    
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">用户名</label>
        <input 
          type="text" 
          id="username" 
          v-model="username" 
          required 
          placeholder="请输入用户名"
        />
      </div>
      
      <div class="form-group">
        <label for="password">密码</label>
        <input 
          type="password" 
          id="password" 
          v-model="password" 
          required 
          placeholder="请输入密码"
        />
      </div>
      
      <div class="form-actions">
        <button 
          type="submit" 
          class="btn-login" 
          :disabled="userStore.isLoading"
        >
          {{ userStore.isLoading ? '登录中...' : '登录' }}
        </button>
        <button 
          type="button" 
          class="btn-cancel" 
          @click="$emit('cancel')"
          :disabled="userStore.isLoading"
        >
          取消
        </button>
      </div>
    </form>
    
    <div class="form-footer">
      <p>还没有账号？ <a href="#" @click.prevent="$emit('switch-to-register')">立即注册</a></p>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { useUserStore } from '@/stores/userStore'

export default defineComponent({
  name: 'LoginForm',
  emits: ['login-success', 'cancel', 'switch-to-register'],
  setup(props, { emit }) {
    const userStore = useUserStore()
    const username = ref('')
    const password = ref('')
    
    const handleLogin = async () => {
      const success = await userStore.login(username.value, password.value)
      if (success) {
        emit('login-success')
      }
    }
    
    return {
      userStore,
      username,
      password,
      handleLogin
    }
  }
})
</script>

<style scoped>
.login-form {
  background-color: #2a475e;
  padding: 2rem;
  border-radius: 8px;
  width: 100%;
  max-width: 400px;
}

h2 {
  margin-top: 0;
  color: #ffffff;
  text-align: center;
  margin-bottom: 1.5rem;
}

.error-message {
  background-color: rgba(194, 59, 34, 0.5);
  color: #ffffff;
  padding: 0.8rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #c7d5e0;
  font-size: 0.9rem;
}

input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #387198;
  background-color: #1b2838;
  color: #ffffff;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: #66c0f4;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-login, .btn-cancel {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  flex: 1;
}

.btn-login {
  background-color: #5c7e10;
  color: white;
}

.btn-login:hover {
  background-color: #6d9619;
}

.btn-cancel {
  background-color: #32404d;
  color: #c7d5e0;
}

.btn-cancel:hover {
  background-color: #3d4c5c;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.form-footer {
  margin-top: 1.5rem;
  text-align: center;
  color: #8f98a0;
  font-size: 0.9rem;
}

.form-footer a {
  color: #66c0f4;
  text-decoration: none;
}

.form-footer a:hover {
  text-decoration: underline;
}
</style>