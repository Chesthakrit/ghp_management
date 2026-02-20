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

        <p class="switch-text">
          Don't have an account? <span @click="handleRegisterClick">Register here</span>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'
import logo from '../assets/ghp-logo.png'

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

        const response = await axios.post('http://127.0.0.1:8000/auth/login', formData)

        if (response.data.access_token) {
            localStorage.setItem('token', response.data.access_token)

            Swal.fire({
                icon: 'success',
                title: 'Login Successful',
                text: 'Redirecting to Dashboard...',
                timer: 1000,
                showConfirmButton: false
            }).then(() => {
                emit('go-to-dashboard')
            })
        }
    } catch (error) {
        console.error('Login Error:', error)
        
        let title = 'Login Failed'
        let text = 'Invalid username or password'

        if (error.response) {
            if (error.response.status === 500) {
                title = 'Server Error'
                text = 'Database connection or schema error. Please contact admin.'
            } else if (error.response.data && error.response.data.detail) {
                text = error.response.data.detail
            }
        }

        Swal.fire({
            icon: 'error',
            title: title,
            text: text
        })
    }
}

const handleRegisterClick = async () => {
    const { value: adminCode } = await Swal.fire({
        title: 'Admin Authorization Required',
        input: 'password',
        inputLabel: 'Enter Admin Code to register new employee',
        inputPlaceholder: 'Admin Code',
        showCancelButton: true,
        inputValidator: (value) => {
            if (!value) {
                return 'You need to write something!'
            }
        }
    })

    if (adminCode) {
        try {
            await axios.post('http://127.0.0.1:8000/auth/verify-admin-code', { code: adminCode })
            emit('go-to-register')
        } catch (error) {
            Swal.fire({
                icon: 'error',
                title: 'Access Denied',
                text: 'Incorrect Admin Code'
            })
        }
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
    background: #1a2a3a;
    color: white;
    border: none;
    border-radius: 25px;
    cursor: pointer;
}

.switch-text {
    margin-top: 20px;
    font-size: 14px;
    color: #666;
}

.switch-text span {
    color: #4a90e2;
    cursor: pointer;
    font-weight: bold;
}
</style>
