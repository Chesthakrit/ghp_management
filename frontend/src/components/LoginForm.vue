<template>
  <div class="login-wrapper">
    
    <div class="login-card">

      <div class="logo-section">
        <img src="C:\Users\mangc\Desktop\project_all\ghp_management\frontend\src\assets\ghp-logo.png" alt="GHP Logo" class="app-logo" />
      </div>

      <div class="login-body">
        <div class="header-section">
          <h1 class="login-title">Login</h1>
          <p class="login-subtitle">Please Sign in to continue.</p>
        </div>

        <div class="input-group">
          
          <input 
            type="text" 
            v-model="username" 
            placeholder="Username" 
            class="custom-input" 
          />
          
          <div class="password-field">
            <input 
              :type="isPasswordVisible ? 'text' : 'password'" 
              v-model="password" 
              placeholder="Password" 
              class="custom-input" 
            />
            <span class="eye-icon" @click="togglePassword">
              {{ isPasswordVisible ? '👁️' : '🙈' }}
            </span>
          </div>

          <div class="options-container">
            <label class="remember-me">
              <input type="checkbox" v-model="rememberMe" />
              <span>Remember me</span>
            </label>
            <a href="#" class="forgot-link">Forgot Password?</a>
          </div>
        </div>

        <button class="signin-button" @click="handleLogin">
          Sign In
        </button>

        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

        <p class="company-footer">Goodhome Professional Group.</p>
      </div>

    </div>
  </div>
</template>

<script setup>
/**
 * การนำเข้า (Import) สิ่งที่จำเป็น
 * ref: ใช้สร้างตัวแปรที่เปลี่ยนแปลงค่าได้และหน้าจอจะอัปเดตตาม
 */
import { ref } from 'vue'

// --- การประกาศตัวแปร (Variables) ---
const username = ref('')
const password = ref('')
const rememberMe = ref(false)
const isPasswordVisible = ref(false) // สถานะดวงตา
const errorMessage = ref('')

// สัญญาณส่งไปหา App.vue
const emit = defineEmits(['login-success'])

/**
 * ฟังก์ชันสลับการมองเห็นรหัสผ่าน
 */
const togglePassword = () => {
  isPasswordVisible.value = !isPasswordVisible.value
}

/**
 * ฟังก์ชันจัดการการล็อกอิน (Logic)
 */
const handleLogin = () => {
  // ตรวจสอบความว่างเปล่า
  if (!username.value || !password.value) {
    errorMessage.value = 'กรุณากรอกข้อมูลให้ครบถ้วนครับ ช่างกิ๊บ'
    return
  }

  // ตรวจสอบ Username/Password จำลอง
  if (username.value === 'admin' && password.value === '1234') {
    errorMessage.value = ''
    emit('login-success')
  } else {
    errorMessage.value = 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'
  }
}
</script>

<style scoped>
/* --- 1. สไตล์สำหรับ iPhone (Mobile First) --- */
.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
}

.login-card {
  background-color: #ffffff;
  border-radius: 40px;
  width: 100%;
  max-width: 100%;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.4);
  overflow: hidden;
  padding-bottom: 20px;
}

.logo-section {
  padding-top: 50px;
  display: flex;
  justify-content: center;
}

.app-logo {
  height: 80px;
  width: auto;
}

.login-body {
  padding: 20px 30px 40px;
  text-align: center;
}

.login-title {
  font-family: 'Kanit', sans-serif;
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 5px;
}

.login-subtitle {
  font-size: 14px;
  color: #999;
  margin-bottom: 35px;
}

/* ช่องกรอกข้อมูล */
.custom-input {
  width: 100%;
  padding: 18px 25px;
  border: 1px solid #f0f0f0;
  border-radius: 20px;
  background-color: #fcfcfc;
  margin-bottom: 15px;
  box-sizing: border-box;
}

/* ส่วนของรหัสผ่านที่มีดวงตา */
.password-field {
  position: relative;
}

.password-field .custom-input {
  padding-right: 60px; /* เว้นที่ให้ดวงตา */
}

.eye-icon {
  position: absolute;
  right: 20px;
  top: 40%;
  transform: translateY(-50%);
  cursor: pointer;
  font-size: 20px;
  user-select: none;
}

/* Options */
.options-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 0 5px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
}

.forgot-link {
  font-size: 13px;
  color: #1a2a3a;
  text-decoration: none;
  font-weight: 600;
}

/* ปุ่ม Sign In */
.signin-button {
  width: 100%;
  padding: 18px;
  background-color: #1a2a3a;
  color: white;
  border: none;
  border-radius: 30px;
  font-weight: 600;
  cursor: pointer;
}

.error-text {
  color: #e74c3c;
  font-size: 13px;
  margin-top: 15px;
}

.company-footer {
  font-size: 12px;
  color: #ccc;
  margin-top: 35px;
}

/* --- 2. สไตล์สำหรับ iPad (Tablet) --- */
@media (min-width: 768px) {
  .login-card {
    max-width: 480px;
  }
}

/* --- 3. สไตล์สำหรับ Desktop (PC) --- */
@media (min-width: 1024px) {
  .login-card {
    max-width: 550px;
  }
  .app-logo {
    height: 100px;
  }
  .login-body {
    padding: 30px 70px 50px;
  }
}
</style>