<!-- 
  ไฟล์: frontend/src/App.vue
  หน้าที่: เป็นหน้าหลักของโปรแกรม (Root Component) ที่รวมทุกหน้าไว้ด้วยกัน
  รายละเอียด:
  - ทำหน้าที่เป็น "ตัวกลาง" ในการสลับหน้าระหว่าง "หน้าล็อกอิน" (LoginForm) และ "หน้าสมัครสมาชิก" (RegisterForm)
  - เก็บสถานะ (State) ว่าตอนนี้ควรโชว์หน้าไหน (currentView)
  - รับคำสั่งจากหน้าลูกๆ (Event) ว่าให้เปลี่ยนไปหน้าไหน
-->
<script setup>
/**
 * การอิมพอร์ต (Import [การนำเข้า]) สิ่งที่จำเป็น
 */
import { ref } from 'vue'
import LoginForm from './components/LoginForm.vue'
import RegisterForm from './components/RegisterForm.vue'
import Dashboard from './components/Dashboard.vue'
import AdminPanel from './components/AdminPanel.vue'
import EmployeeIdentityEditor from './components/EmployeeIdentityEditor.vue'

// ตัวแปรควบคุมหน้าจอ: 'login' หรือ 'register'
// ตรวจสอบ Token ใน localStorage เพื่อคงสถานะล็อกอิน
const token = localStorage.getItem('token')
const savedView = localStorage.getItem('last_view') // อ่านค่าหน้าล่าสุดที่เปิดค้างไว้

// ถ้ามี token -> ไป dashboard
// ถ้าไม่มี token และ last_view เป็น register -> ไป register
// นอกนั้น -> ไป login
const getInitialView = () => {
  if (token) return 'dashboard'
  if (savedView === 'register') return 'register'
  return 'login'
}

const currentView = ref(getInitialView())
const selectedUserId = ref(null)

/**
 * ฟังก์ชันสลับหน้า
 * @param {String} pageName - ชื่อหน้าที่ต้องการไป
 */
const goToPage = (pageName, userId = null) => {
  currentView.value = pageName
  selectedUserId.value = userId
  localStorage.setItem('last_view', pageName) // บันทึกหน้าปัจจุบันลง localStorage
}
</script>

<template>
  <div class="app-container">
    <LoginForm 
      v-if="currentView === 'login'" 
      @go-to-register="goToPage('register')" 
      @go-to-dashboard="goToPage('dashboard')"
    />

    <RegisterForm 
      v-else-if="currentView === 'register'" 
      @go-to-login="goToPage('login')" 
    />

    <Dashboard 
      v-else-if="currentView === 'dashboard'" 
      @go-to-login="goToPage('login')"
      @go-to-admin="goToPage('admin')"
    />

    <AdminPanel
      v-else-if="currentView === 'admin'"
      @go-back="goToPage('dashboard')"
      @go-to-identity="(id) => goToPage('identity', id)"
    />

    <EmployeeIdentityEditor
      v-else-if="currentView === 'identity'"
      :initialUserId="selectedUserId"
      @go-back="goToPage('admin')"
    />
  </div>
</template>

<style>
/* ล้างค่าขอบเดิมและตั้งพื้นหลัง */
body {
  margin: 0;
  background-color: #1a1a1a;
  font-family: 'Kanit', sans-serif;
}
.app-container {
  min-height: 100vh;
}
</style>