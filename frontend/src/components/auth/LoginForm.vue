<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="logo-section">
        <img :src="logo" alt="Logo" class="app-logo" />
      </div>

      <div class="login-body">
        <h1 class="login-title">Login</h1>
        
        <div class="input-group">
          <input 
            type="text" 
            v-model="username" 
            placeholder="Username" 
            class="custom-input" 
            autocomplete="off"
          />
          
          <div class="password-field">
            <input 
              :type="isPasswordVisible ? 'text' : 'password'" 
              v-model="password" 
              placeholder="Password" 
              class="custom-input" 
              autocomplete="new-password"
            />
            <span class="eye-icon" @click="isPasswordVisible = !isPasswordVisible">
              {{ isPasswordVisible ? '👁️' : '🙈' }}
            </span>
          </div>
        </div>

        <button class="signin-button" @click="handleLogin">Sign In</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'
import Swal from 'sweetalert2'
import logo from '../../assets/ghp-logo.png'

const emit = defineEmits(['go-to-register', 'go-to-dashboard'])

// --- Logic from LoginForm.js ---
const username = ref('')
const password = ref('')
const isPasswordVisible = ref(false)

onMounted(() => {
    username.value = ''
    password.value = ''
})

const handleLogin = async () => {
    try {
        const formData = new FormData()
        formData.append('username', username.value)
        formData.append('password', password.value)

        const response = await api.post('/auth/login', formData)

        if (response.data.access_token) {
            localStorage.setItem('token', response.data.access_token)

            // ดึงข้อมูล User ล่าสุดเพื่อดู Role และ Permissions
            const userRes = await api.get('/users/me')
            const userData = {
                username: username.value,
                role: userRes.data.role,
                permissions: userRes.data.permissions || [],
                access_token: response.data.access_token
            }

            // เก็บใส่ localStorage เพื่อเอามาใช้งานที่หน้าบ้าน (Frontend)
            localStorage.setItem('username', userData.username)
            localStorage.setItem('user_role', userData.role)
            localStorage.setItem('user_permissions', JSON.stringify(userData.permissions))

            Swal.fire({
                icon: 'success',
                title: 'Login Successful',
                text: 'Redirecting...',
                timer: 1000,
                showConfirmButton: false
            }).then(() => {
                emit('go-to-dashboard', userData)
            })
        }
    } catch (error) {
        console.error('Login Error:', error)
        
        let title = 'Login Failed'
        let text = 'Username or password incorrect.'

        if (error.response) {
            // API returned an error
            text = error.response.data.detail || 'Invalid Credentials';
        } else if (error.request) {
            // No response received (Network failure)
            text = 'Network Error: Cannot connect to server. Please check your connection or IP configuration.';
        } else {
            text = error.message;
        }

        Swal.fire({
            icon: 'error',
            title: title,
            text: text
        })
    }
}
</script>

<style scoped>
/* --- Styles from LoginForm.css --- */
.login-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}

.login-card {
    background: white;
    border-radius: 40px;
    padding: 40px;
    width: 400px;
    text-align: center;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
}

.app-logo {
    height: 80px;
    margin-bottom: 20px;
}

.custom-input {
    width: 100%;
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 15px;
    border: 1px solid #eee;
    box-sizing: border-box;
}

.password-field {
    position: relative;
}

.eye-icon {
    position: absolute;
    right: 15px;
    top: 15px;
    cursor: pointer;
}

.signin-button {
    width: 100%;
    padding: 15px;
    background: #e53e3e;
    color: white;
    border: none;
    border-radius: 25px;
    cursor: pointer;
}
</style>
