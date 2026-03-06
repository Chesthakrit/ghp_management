<template>
    <div class="user-profile-layout">
    <!-- ─── 1. Top Navbar ─── -->
    <header class="profile-header">
      <div class="header-left">
        <button class="sidebar-toggle" @click="toggleSidebar">
          <i class="fas fa-bars"></i>
        </button>
        <div class="ghp-logo">GHP</div>
        <span class="brand-name">MANAGEMENT</span>
      </div>
      <div class="header-right">
        <button v-if="isAdmin" class="admin-panel-btn" @click="handleBack">
          <i class="fas fa-tools"></i> Admin Panel
        </button>
        <button class="logout-btn" @click="handleLogout">
          <i class="fas fa-sign-out-alt"></i> Logout
        </button>
      </div>
    </header>

    <div class="layout-container">
      <!-- ─── 2. Left Sidebar ─── -->
      <aside class="sidebar" :class="{ 'collapsed': !isSidebarOpen, 'mobile-open': isSidebarOpen }">
        <div class="sidebar-user-glance" v-if="isSidebarOpen">
          <div class="mini-avatar">
            <img v-if="user?.photo_path" :src="`${apiBase}/${user.photo_path}`" />
            <span v-else>{{ user?.first_name?.[0] }}</span>
          </div>
          <div class="mini-info">
            <div class="mini-name">{{ user?.first_name }}</div>
            <div class="mini-role">{{ user?.employee_profile?.job_title }}</div>
          </div>
        </div>

        <nav class="sidebar-nav">
          <button 
            v-for="item in menuItems" 
            :key="item.id"
            :class="['nav-item', { active: activeMenu === item.id }]"
            @click="activeMenu = item.id; if (isMobile) isSidebarOpen = false"
          >
            <i :class="item.icon"></i>
            <span v-if="isSidebarOpen">{{ item.label }}</span>
          </button>
        </nav>
      </aside>

      <!-- Mobile Overlay -->
      <div v-if="isSidebarOpen && isMobile" class="sidebar-overlay" @click="isSidebarOpen = false"></div>


      <!-- ─── 3. Main Content Area ─── -->
      <main class="main-content">
        <!-- Loading State -->
        <div v-if="isLoading" class="profile-loading">
          <div class="loader-spinner"></div>
          <p>Loading data...</p>
        </div>

        <template v-else-if="user">
          <!-- Profile Header (Always visible or shows active component) -->
        <div class="content-header-banner" v-if="activeMenu === 'profile'">
          <div class="profile-info-status">
            <div class="profile-pic-container">
              <div class="profile-pic-wrapper">
                <img v-if="user?.photo_path" :src="`${apiBase}/${user.photo_path}`" class="profile-pic" />
                <div v-else class="profile-placeholder">{{ user?.username?.[0]?.toUpperCase() }}</div>
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

        <div class="content-body">
          <div v-if="activeMenu === 'profile'" class="profile-details-grid">
            <!-- Example stats or details -->
            <div class="detail-card">
              <h3>Personal Information</h3>
              <div class="info-row"><span>Nickname:</span> <strong>{{ user?.nickname || '-' }}</strong></div>
              <div class="info-row"><span>Full Name:</span> <strong>{{ user?.first_name }} {{ user?.last_name }}</strong></div>
              <div class="info-row"><span>Employee ID:</span> <strong>{{ user?.username }}</strong></div>
            </div>
            <div class="detail-card">
              <h3>Employment Information</h3>
              <div class="info-row"><span>Department:</span> <strong>{{ user?.employee_profile?.department }}</strong></div>
              <div class="info-row"><span>Job Title:</span> <strong>{{ user?.employee_profile?.job_title }}</strong></div>
              <div class="info-row"><span>Hire Date:</span> <strong>{{ formatDate(user?.employee_profile?.hire_date) }}</strong></div>
            </div>
          </div>

          <div v-else class="empty-content-state">
            <i :class="currentMenuIcon"></i>
            <h2>{{ currentMenuLabel }}</h2>
            <p>No data available for {{ currentMenuLabel }} at the moment.</p>
          </div>
        </div>
        </template>

        <div v-else class="profile-error">
           <i class="fas fa-exclamation-circle"></i>
           <h2>User Not Found</h2>
           <p>Error fetching data or user does not exist in the system.</p>
           <button class="btn-retry" @click="fetchUserData">Try Again</button>
        </div>
      </main>
    </div>
  </div>

</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../api'

const props = defineProps(['username', 'userId'])
const emit = defineEmits(['go-back', 'logout'])

const apiBase = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'
const user = ref(null)
const isLoading = ref(false)
const isSidebarOpen = ref(window.innerWidth > 768)
const isMobile = ref(window.innerWidth <= 768)
const activeMenu = ref('profile')

const menuItems = [
  { id: 'profile', label: 'Profile', icon: 'fas fa-user-circle' },
  { id: 'schedule', label: 'Schedule', icon: 'fas fa-calendar-alt' },
  { id: 'payslip', label: 'Payslip', icon: 'fas fa-file-invoice-dollar' },
  { id: 'attendance', label: 'Attendance', icon: 'fas fa-clock' },
  { id: 'documents', label: 'Documents', icon: 'fas fa-book' },
]

const currentMenuLabel = computed(() => menuItems.find(m => m.id === activeMenu.value)?.label)
const currentMenuIcon = computed(() => menuItems.find(m => m.id === activeMenu.value)?.icon)

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const isAdmin = computed(() => {
  // Check if LOGGED-IN user is admin (from localStorage)
  const role = (localStorage.getItem('user_role') || '').toLowerCase()
  const uname = (localStorage.getItem('username') || '').toLowerCase()
  return role === 'admin' || uname === 'admin'
})

const fetchUserData = async () => {
  isLoading.value = true
  user.value = null
  try {
    // If we're loading a new user, reset to profile tab
    activeMenu.value = 'profile'
    
    // If props.userId is provided, fetch that specific user (Admin viewing someone)
    // Otherwise, fetch /users/me (Standard logged-in flow)
    const endpoint = props.userId ? `/users/${props.userId}` : '/users/me'
    const res = await api.get(endpoint)
    user.value = res.data
  } catch (err) {
    console.error('Error fetching user profile:', err)
  } finally {
    isLoading.value = false
  }
}

// Watch for userId changes so we refresh data if admin switches users
watch(() => props.userId, () => {
  fetchUserData()
})

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('th-TH', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

const handleLogout = () => emit('logout')
const handleBack = () => emit('go-back')

const handleResize = () => {
  isMobile.value = window.innerWidth <= 768
  if (!isMobile.value) {
    isSidebarOpen.value = true
  } else {
    isSidebarOpen.value = false
  }
}

onMounted(() => {
  fetchUserData()
  window.addEventListener('resize', handleResize)
  handleResize()
})

</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600&display=swap');

.user-profile-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
  font-family: 'Kanit', sans-serif;
  color: #1e293b;
}

/* ─── Header ─── */
.profile-header {
  height: 64px;
  background: #0f172a;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  z-index: 50;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.sidebar-toggle {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.sidebar-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.ghp-logo {
  background: #3b82f6;
  color: white;
  padding: 4px 12px;
  border-radius: 8px;
  font-weight: 800;
  font-size: 1.1rem;
}

.brand-name {
  font-weight: 600;
  font-size: 0.875rem;
  letter-spacing: 0.1em;
  color: #94a3b8;
}
.header-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.admin-panel-btn {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  padding: 8px 16px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.admin-panel-btn:hover {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.logout-btn {
  background: rgba(239, 44, 44, 0.1);
  border: 1px solid rgba(239, 44, 44, 0.2);
  color: #f87171;
  padding: 8px 16px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: #ef4444;
  color: #fff;
  border-color: #ef4444;
}

/* ─── Layout Container ─── */
.layout-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* ─── Sidebar ─── */
.sidebar {
  width: 260px;
  background: #fff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 40;
}

.sidebar.collapsed {
  width: 80px;
}

.sidebar-user-glance {
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid #f1f5f9;
}

.mini-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #f1f5f9;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.mini-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.mini-avatar span {
  font-weight: 600;
  color: #64748b;
}

.mini-info {
  overflow: hidden;
}

.mini-name {
  font-weight: 600;
  font-size: 0.9375rem;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mini-role {
  font-size: 0.75rem;
  color: #64748b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-nav {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: none;
  background: transparent;
  color: #64748b;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  font-family: inherit;
  font-weight: 500;
}

.nav-item i {
  font-size: 1.25rem;
  width: 24px;
  text-align: center;
}

.nav-item:hover {
  background: #f1f5f9;
  color: #1e293b;
}

.nav-item.active {
  background: #eff6ff;
  color: #3b82f6;
}

/* ─── Main Content ─── */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.content-header-banner {
  background: #fff;
  padding: 32px;
  border-radius: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.profile-info-status {
  display: flex;
  align-items: center;
  gap: 24px;
}

.profile-pic-container {
  position: relative;
}

.profile-pic-wrapper {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 4px solid #fff;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  background: #f8fafc;
}

.profile-pic { width: 100%; height: 100%; object-fit: cover; }
.profile-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  font-size: 3rem; font-weight: 700; color: #cbd5e0;
}

.photo-edit-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #3b82f6;
  color: #fff;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid #fff;
  cursor: pointer;
  font-size: 0.875rem;
}

.profile-name {
  margin: 0 0 4px 0;
  font-size: 1.875rem;
  font-weight: 700;
  color: #1e293b;
}

.profile-sub-info {
  display: flex;
  gap: 16px;
}

.info-text {
  font-size: 0.9375rem;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 6px;
}

.info-text::before {
  content: '•';
  color: #cbd5e0;
}
.info-text:first-child::before { display: none; }

/* ─── Content Body ─── */
.profile-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.detail-card {
  background: #fff;
  padding: 24px;
  border-radius: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.detail-card h3 {
  margin: 0 0 20px 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 0.9375rem;
}

.info-row span { color: #64748b; }
.info-row strong { color: #1e293b; font-weight: 500; }

.empty-content-state {
  text-align: center;
  padding: 80px 0;
  color: #94a3b8;
}

.empty-content-state i {
  font-size: 4rem;
  margin-bottom: 24px;
  opacity: 0.2;
}

/* Responsiveness */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    height: 100vh;
    left: 0;
    top: 64px;
    transform: translateX(-100%);
  }
  .sidebar.mobile-open {
    transform: translateX(0);
    width: 260px !important;
  }
  .sidebar.collapsed { 
    transform: translateX(-100%);
    width: 0; 
    padding: 0; 
    overflow: hidden; 
    border: none; 
  }
  .sidebar-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 35;
    backdrop-filter: blur(2px);
  }
  .main-content { padding: 20px; }
  .profile-info-status { flex-direction: column; text-align: center; }
  .profile-sub-info { justify-content: center; flex-wrap: wrap; }
}

/* Loading & Error States */
.profile-loading, .profile-error {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #64748b;
  gap: 16px;
  padding: 40px;
}
.loader-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f1f5f9;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.profile-error i {
  font-size: 3rem;
  color: #ef4444;
}
.btn-retry {
  padding: 8px 20px;
  background: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-family: inherit;
}
</style>
