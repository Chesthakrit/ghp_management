<template>
  <div class="user-profile-layout">
    <!-- ─── 1. Top Navbar ─── -->
    <header class="profile-header">
      <div class="header-left">
        <div class="ghp-logo" @click="handleBack">GHP</div>
        <span class="brand-name">MANAGEMENT</span>
      </div>
      <div class="header-right">
        <button class="logout-btn" @click="handleLogout">
          <i class="fas fa-sign-out-alt"></i> Logout
        </button>
      </div>
    </header>

    <div class="profile-body-container">
      <div class="profile-view-content">
        <!-- ─── Profile Info Left Aligned ─── -->
        <div class="profile-info-status">
          <div class="profile-pic-container">
            <div class="profile-pic-wrapper">
              <img v-if="user?.photo_path" :src="`${apiBase}/${user.photo_path}`" class="profile-pic" />
              <div v-else class="profile-placeholder">{{ username?.[0]?.toUpperCase() }}</div>
            </div>
            <div class="photo-edit-badge">
              <i class="fas fa-camera"></i>
            </div>
          </div>
          
          <div class="profile-info-column">
            <h1 class="profile-name">{{ user?.first_name }} {{ user?.last_name }}</h1>
            <div class="profile-sub-info">
              <div class="info-text">{{ user?.employee_profile?.job_title || 'Role' }}</div>
              <div class="info-text">{{ user?.employee_profile?.department || 'Department' }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- ─── RIGHT CONTENT: Placeholder for other menus ─── -->
      <main class="content-area">
        <div class="empty-content-state">
          <i class="fas fa-th-large"></i>
          <h2>เมนูพนักงาน</h2>
          <p>เลือกเมนูที่ต้องการแสดงผลในพื้นที่นี้</p>
          
          <div class="menu-placeholders-grid">
            <div class="menu-box">
              <i class="fas fa-calendar-alt"></i>
              <span>ตารางงาน</span>
            </div>
            <div class="menu-box">
              <i class="fas fa-file-invoice"></i>
              <span>ใบแจ้งเงินเดือน</span>
            </div>
            <div class="menu-box">
              <i class="fas fa-clock"></i>
              <span>บันทึกเวลา</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const props = defineProps(['username'])
const emit = defineEmits(['go-back', 'logout'])

const apiBase = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'
const user = ref(null)

const fetchUserData = async () => {
  try {
    const res = await api.get('/users/me')
    user.value = res.data
  } catch (err) {
    console.error('Error fetching user profile:', err)
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('th-TH', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const handleLogout = () => emit('logout')
const handleBack = () => emit('go-back')

onMounted(() => {
  fetchUserData()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600&display=swap');

.user-profile-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f4f7f9;
  font-family: 'Kanit', sans-serif;
  color: #2c3e50;
}

/* ─── Header ─── */
.profile-header {
  height: 60px;
  background: #1a2a3a;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  z-index: 10;
}
.header-left { display: flex; align-items: center; gap: 15px; cursor: pointer; }
.ghp-logo {
  background: #3498db;
  color: white;
  padding: 5px 10px;
  border-radius: 8px;
  font-weight: 800;
  font-size: 1.2rem;
}
.brand-name { font-weight: 600; font-size: 0.9rem; letter-spacing: 2px; }
.logout-btn {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.3);
  color: #fff;
  padding: 6px 15px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}
.logout-btn:hover { background: #e74c3c; border-color: #e74c3c; }

/* ─── Body Layout ─── */
.profile-body-container {
  flex: 1;
  background: white; /* Clean white background */
  overflow-y: auto;
  padding: 15px 25px; /* Minimal padding for left alignment */
}

.profile-view-content {
  width: 100%;
}

/* ─── Profile Info Left Aligned ─── */
.profile-info-status {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f1f5f9;
}

.profile-pic-container {
  position: relative;
  flex-shrink: 0;
}

.profile-pic-wrapper {
  width: 150px;
  height: 150px;
  background: #f8fafc;
  border-radius: 50%;
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.profile-pic {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  font-size: 2.5rem; font-weight: 700; color: #cbd5e0;
}

.photo-edit-badge {
  position: absolute;
  bottom: 5px;
  right: 5px;
  background: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  border: 1px solid #e2e8f0;
  color: #1a4d33;
  font-size: 0.8rem;
}

.profile-info-column {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.profile-name {
  margin: 0;
  font-size: 1.5rem;
  color: #1a4d33; /* Green name from image */
  font-weight: 600;
}

.profile-sub-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-text {
  font-size: 1rem;
  color: #64748b;
  font-weight: 400;
}

/* ─── Right Content Area ─── */
.content-area {
  flex: 1;
  padding: 40px;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-content-state {
  text-align: center;
  color: #94a3b8;
  max-width: 500px;
}
.empty-content-state i { font-size: 4rem; margin-bottom: 20px; color: #e2e8f0; }
.empty-content-state h2 { color: #475569; margin-bottom: 10px; }

.menu-placeholders-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-top: 30px;
}
.menu-box {
  background: white;
  padding: 20px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  border: 1px dashed #cbd5e0;
  cursor: pointer;
  transition: all 0.2s;
}
.menu-box:hover { border-color: #3498db; color: #3498db; transform: scale(1.05); }
.menu-box i { font-size: 1.5rem; }
.menu-box span { font-size: 0.85rem; font-weight: 500; }

@media (max-width: 850px) {
  .profile-top-banner { padding: 15px; }
  .profile-info-status { gap: 15px; }
  .profile-pic-wrapper { width: 120px; height: 120px; }
  .profile-name { font-size: 1.3rem; }
  .content-area { padding: 20px; }
}
</style>
