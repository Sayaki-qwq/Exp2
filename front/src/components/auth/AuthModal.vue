<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <button class="modal-close" @click="$emit('close')">&times;</button>
      
      <LoginForm 
        v-if="activeForm === 'login'" 
        @login-success="handleLoginSuccess" 
        @cancel="$emit('close')"
        @switch-to-register="activeForm = 'register'"
      />
      
      <RegisterForm 
        v-else 
        @register-success="handleRegisterSuccess" 
        @cancel="$emit('close')"
        @switch-to-login="activeForm = 'login'"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import LoginForm from './LoginForm.vue'
import RegisterForm from './RegisterForm.vue'

export default defineComponent({
  name: 'AuthModal',
  components: {
    LoginForm,
    RegisterForm
  },
  props: {
    initialForm: {
      type: String,
      default: 'login',
      validator: (value: string) => ['login', 'register'].includes(value)
    }
  },
  emits: ['close', 'login-success', 'register-success'],
  setup(props, { emit }) {
    const activeForm = ref(props.initialForm)
    
    const handleLoginSuccess = () => {
      emit('login-success')
      emit('close')
    }
    
    const handleRegisterSuccess = () => {
      emit('register-success')
    }
    
    return {
      activeForm,
      handleLoginSuccess,
      handleRegisterSuccess
    }
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  position: relative;
  max-width: 90%;
  max-height: 90%;
  overflow-y: auto;
  animation: modal-in 0.3s ease-out;
}

.modal-close {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #8f98a0;
  cursor: pointer;
  z-index: 10;
}

.modal-close:hover {
  color: #ffffff;
}

@keyframes modal-in {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>