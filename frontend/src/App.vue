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
import AdminPanel from './components/AdminPanel.vue'
import EmployeeIdentityEditor from './components/EmployeeIdentityEditor.vue'
import UserProfile from './components/UserProfile.vue'

// ตัวแปรควบคุมหน้าจอ: 'login' หรือ 'register'
// ตรวจสอบ Token ใน localStorage เพื่อคงสถานะล็อกอิน
const token = localStorage.getItem('token')
const userRole = ref(localStorage.getItem('user_role'))
const username = ref(localStorage.getItem('username') || '')
const savedView = localStorage.getItem('last_view') // อ่านค่าหน้าล่าสุดที่เปิดค้างไว้

// ถ้ามี token -> ตรวจสอบ role
const getInitialView = () => {
  const currentRole = (userRole.value || '').toLowerCase()
  const currentUsername = (username.value || '').toLowerCase()
  
  console.log("App.vue DEBUG - Initial Load:", { 
    token: !!token, 
    role: currentRole, 
    username: currentUsername 
  })

  if (token) {
    // ถ้าเป็น admin (เช็คจาก Role หรือ Username ก็ได้ เพื่อความชัวร์)
    if (currentRole === 'admin' || currentUsername === 'admin') {
      console.log("App.vue DEBUG - Redirecting to: admin")
      return 'admin'
    }
    console.log("App.vue DEBUG - Redirecting to: profile")
    return 'profile'
  }
  
  if (savedView === 'register') return 'register'
  return 'login'
}

const currentView = ref(getInitialView())
const selectedUserId = ref(null)

/**
 * ฟังก์ชันสลับหน้า
 * @param {String} pageName - ชื่อหน้าที่ต้องการไป
 */
const goToPage = (pageName, userId = null, userData = null) => {
  console.log(`App.vue DEBUG - Navigating to ${pageName} for user:`, userId)
  let targetPage = pageName

  // ถ้ามีการส่งข้อมูล User มา (เช่น ตอน Login) ให้ตรวจสอบสิทธิ์ตรงนั้นเลย
  if (userData) {
    const role = (userData.role || '').toLowerCase()
    const uName = (userData.username || '').toLowerCase()
    
    if (role === 'admin' || uName === 'admin') {
      targetPage = 'admin'
    }

    username.value = userData.username
    userRole.value = userData.role
    localStorage.setItem('username', userData.username)
    localStorage.setItem('user_role', userData.role)
    if (userData.access_token) {
      localStorage.setItem('token', userData.access_token)
    }
  }

  // ถ้า targetPage ยังเป็น dashboard ให้เปลี่ยนเป็น profile ทันที (เพราะเราเลิกใช้ dashboard แล้ว)
  if (targetPage === 'dashboard') targetPage = 'profile'

  currentView.value = targetPage
  selectedUserId.value = userId
  localStorage.setItem('last_view', targetPage)
}

const handleLogout = () => {
  localStorage.clear()
  currentView.value = 'login'
}
</script>

<template>
  <div class="app-container">
    <LoginForm 
      v-if="currentView === 'login'" 
      @go-to-register="goToPage('register')" 
      @go-to-dashboard="(data) => goToPage('profile', null, data)"
    />

    <RegisterForm 
      v-else-if="currentView === 'register'" 
      @go-to-login="goToPage('login')" 
    />


    <AdminPanel
      v-else-if="currentView === 'admin'"
      @logout="handleLogout"
      @go-to-profile="goToPage('profile')"
      @view-profile="(id) => goToPage('profile', id)"
      @go-to-identity="(id) => goToPage('identity', id)"
    />

    <EmployeeIdentityEditor
      v-else-if="currentView === 'identity'"
      :initialUserId="selectedUserId"
      @go-back="goToPage('admin')"
    />

    <UserProfile
      v-else-if="currentView === 'profile'"
      :key="selectedUserId"
      :username="username"
      :userId="selectedUserId"
      @go-back="((userRole || '').toLowerCase() === 'admin' || (username || '').toLowerCase() === 'admin') ? goToPage('admin') : handleLogout()"
      @logout="handleLogout"
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