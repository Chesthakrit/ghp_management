<script setup>
// อิมพอร์ต (Import) ฟังก์ชัน ref เพื่อใช้จัดการสถานะของหน้าจอ
import { ref } from 'vue'
// อิมพอร์ต (Import) ส่วนหน้าจอ Login มาใช้งาน
import LoginForm from './components/LoginForm.vue'

// ตัวแปรสำหรับเช็คสถานะการเข้าสู่ระบบ (false = หน้า Login, true = หน้า Dashboard)
const isLoggedIn = ref(false)

/**
 * ฟังก์ชัน handleLogin: ทำงานเมื่อล็อกอินสำเร็จ
 */
const handleLogin = () => {
  isLoggedIn.value = true // เปลี่ยนสถานะเป็นล็อกอินแล้ว
}
</script>

<template>
  <div class="main-app-container">
    
    <div v-if="!isLoggedIn">
      <LoginForm @login-success="handleLogin" />
    </div>

    <div v-else class="dashboard-placeholder">
      <h1>ยินดีต้อนรับเข้าสู่ระบบ GHP APP</h1>
    </div>

  </div>
</template>

<style>
/* ล้างระยะขอบพื้นฐาน */
body {
  margin: 0;
  padding: 0;
  background-color: #1a1a1a; /* พื้นหลังสีเข้มเพื่อให้กล่องขาวดูลอย */
}

.main-app-container {
  min-height: 100vh;
  font-family: 'Prompt', sans-serif; /* ใช้ฟอนต์ Prompt เป็นหลัก */
}

.dashboard-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  color: white;
}
</style>