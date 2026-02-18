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
          <input type="text" placeholder="Username" class="custom-input" />
          <input type="password" placeholder="Password" class="custom-input" />

          <div class="options-container">
            <label class="remember-me">
              <input type="checkbox" v-model="rememberMe" />
              <span>Remember me</span>
            </label>
            <a href="#" class="forgot-link">Forgot Password?</a>
          </div>
        </div>

        <button class="signin-button" @click="onLoginSubmit">
          Sign In
        </button>

        <p class="company-footer">Goodhome Professional Group.</p>
      </div>

    </div>
  </div>
</template>

<script setup>
// [สำคัญมาก] ต้องอิมพอร์ต ref มาด้วยเพื่อให้ v-model ทำงานได้
import { ref } from 'vue'

// สร้างตัวแปรเก็บสถานะการติ๊ก "จดจำฉัน" (เริ่มเป็น false คือยังไม่ติ๊ก)
const rememberMe = ref(false)

const emit = defineEmits(['login-success'])

/**
 * ฟังก์ชันเมื่อกดปุ่ม Sign In
 */
const onLoginSubmit = () => {
  emit('login-success')
}
</script>

<style scoped>
/* จัดกึ่งกลางหน้าจอ */
.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
}

/* ตัวการ์ดลอย (Floating Card) */
.login-card {
  background-color: #ffffff;
  border-radius: 40px;
  width: 100%;
  max-width: 100%;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.4); /* เงาเข้มเพื่อให้กล่องดูลอย */
  overflow: hidden;
}

/* ส่วนโลโก้ */
.logo-section {
  padding-top: 50px;
  display: flex;
  justify-content: center;
}
.app-logo {
  height: 90px;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
}

/* เนื้อหาภายใน */
.login-body {
  padding: 20px 30px 40px;
  text-align: center;
}

.login-title {
  font-family: 'Kanit', sans-serif;
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
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

/* [สไตล์ที่เพิ่มใหม่] จัดวาง Remember me และ Forgot Password */
.options-container {
  display: flex;
  justify-content: space-between; /* แยกซ้าย-ขวา */
  align-items: center;
  margin-top: 5px;
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

/* ปุ่มกด */
.signin-button {
  width: 100%;
  padding: 18px;
  background-color: #1a2a3a;
  color: white;
  border: none;
  border-radius: 30px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 10px 20px rgba(26, 42, 58, 0.2);
}

.company-footer {
  font-size: 12px;
  color: #ccc;
  margin-top: 35px;
}

/* ปรับขนาดตามหน้าจอ */
@media (min-width: 768px) { .login-card { max-width: 480px; } }
@media (min-width: 1024px) {
  .login-card { max-width: 550px; }
  .app-logo { height: 110px; }
  .login-body { padding: 30px 70px 50px; }
}
</style>