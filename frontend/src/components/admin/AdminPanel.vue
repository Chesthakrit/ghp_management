<template>
  <div :class="['admin-panel', { 'is-embedded': embedded }]">

    <!-- ─── Sidebar (Desktop / iPad) ─── -->
    <aside v-if="!embedded" class="sidebar" :class="{ 'sidebar-open': sidebarOpen }">
      <div class="sidebar-logo">
        <span>Admin Panel</span>
        <button class="sidebar-close-btn" @click="sidebarOpen = false">✕</button>
      </div>
      <nav class="sidebar-nav">
        <button class="nav-item" @click="$emit('go-to-profile'); sidebarOpen = false">
          <i class="fas fa-id-card-alt"></i> Back to Profile
        </button>

        <button
          :class="['nav-item', { active: activeTab === 'users' }]"
          @click="activeTab = 'users'; sidebarOpen = false"
        >
          <i class="fas fa-users-cog"></i> User Management
        </button>

        <button
          :class="['nav-item', { active: activeTab === 'hr' }]"
          @click="activeTab = 'hr'; sidebarOpen = false"
        >
          <i class="fas fa-sliders-h"></i> HR Settings
        </button>

        <button
          :class="['nav-item', { active: activeTab === 'salary' }]"
          @click="activeTab = 'salary'; sidebarOpen = false"
        >
          <i class="fas fa-money-check-alt"></i> Salary Settings
        </button>

        <button
          v-if="isAdmin || hasPerm('page.access')"
          :class="['nav-item', { active: activeTab === 'access' }]"
          @click="activeTab = 'access'; sidebarOpen = false"
        >
          <i class="fas fa-user-shield"></i> Access Control
        </button>

        <button
          :class="['nav-item', { active: activeTab === 'time_leave' }]"
          @click="activeTab = 'time_leave'; sidebarOpen = false"
        >
          <i class="fas fa-clock"></i> Time & Leave
        </button>

        <button
          :class="['nav-item', { active: activeTab === 'policies' }]"
          @click="activeTab = 'policies'; sidebarOpen = false"
        >
          <i class="fas fa-file-contract"></i> Policies Setup
        </button>
      </nav>
      <button class="logout-sidebar-btn" @click="$emit('logout')">
        <i class="fas fa-door-open"></i> Logout System
      </button>
    </aside>

    <div v-if="sidebarOpen && !embedded" class="sidebar-overlay" @click="sidebarOpen = false"></div>

    <div class="main-wrapper">
      <div v-if="!embedded" class="mobile-topbar">
        <button class="mobile-menu-btn" @click="sidebarOpen = true">☰</button>
        <span class="mobile-title">
          {{ 
            activeTab === 'users' ? 'User Management' : 
            activeTab === 'hr' ? 'HR Settings' : 
            activeTab === 'salary' ? 'Salary Settings' : 
            activeTab === 'access' ? 'Access Control' : 
            activeTab === 'time_leave' ? 'Time & Leave' : 
            activeTab === 'policies' ? 'Policy Management' : 'Dashboard'
          }}
        </span>
        <button class="mobile-logout-btn" @click="$emit('logout')" title="Logout">🚪</button>
      </div>

      <main class="admin-content">
        <div v-if="activeTab === 'users'">
          <UserManagement 
            :currentUser="currentUser"
            :isAdmin="isAdmin"
            @go-to-identity="(id) => $emit('go-to-identity', id)"
            @view-profile="(id) => $emit('view-profile', id)"
            @go-to-register="$emit('go-to-register')"
          />
        </div>

        <!-- TAB: HR Settings -->
        <div v-if="activeTab === 'hr'">
          <HRManagement 
            :departments="departments" 
            :jobTitles="rawJobTitles"
            :currentUser="currentUser"
            :isAdmin="isAdmin"
            @refresh="fetchHRData"
          />
        </div>

        <!-- TAB: Salary Settings -->
        <div v-if="activeTab === 'salary'">
          <SalaryManagement 
            :departments="departments" 
            :jobTitles="rawJobTitles" 
            @refresh="fetchHRData" 
          />
        </div>
        
        <!-- TAB: Access Control -->
        <div v-if="activeTab === 'access'">
          <AccessManagement 
            :departments="departments" 
            :job-titles="rawJobTitles"
            :current-user="currentUser"
            :is-admin="isAdmin"
            @refresh="fetchHRData"
          />
        </div>

        <!-- TAB: Time & Leave Settings -->
        <div v-if="activeTab === 'time_leave'">
          <AttendanceSettings />
        </div>

        <!-- TAB: Policy Management -->
        <div v-if="activeTab === 'policies'">
          <PolicyManagement />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import api from '../../api'
import Swal from 'sweetalert2'
import AccessManagement from './AccessManagement.vue'
import UserManagement from '../shared/UserManagement.vue'
import SalaryManagement from '../shared/SalaryManagement.vue'
import HRManagement from '../shared/HRManagement.vue'
import PolicyManagement from '../shared/PolicyManagement.vue'
import AttendanceSettings from '../shared/AttendanceSettings.vue'

const props = defineProps({
  embedded: { type: String, default: null }
})

const emit = defineEmits(['logout', 'go-to-identity', 'go-to-profile', 'view-profile', 'go-to-register'])

const activeTab = ref(props.embedded || 'users')

watch(() => props.embedded, (newVal) => {
  if (newVal) activeTab.value = newVal
})

const sidebarOpen = ref(false)
const currentUser = ref(null)
const isLoading = ref(false)

const isAdmin = computed(() => {
  const role = (currentUser.value?.role || '').toLowerCase()
  const uname = (currentUser.value?.username || '').toLowerCase()
  return role === 'admin' || uname === 'admin'
})

const hasPerm = (p) => {
  if (isAdmin.value) return true
  return (currentUser.value?.permissions || []).includes(p)
}

// Data Fetching Centralized
const departments = ref([])       
const rawJobTitles = ref([])      

const fetchHRData = async () => {
  try {
    const [deptsRes, jobsRes] = await Promise.all([
      api.get('/hr/departments'),
      api.get('/hr/job-titles')
    ])
    const sortedDepts = [...deptsRes.data].sort((a, b) => (a.display_order || 100) - (b.display_order || 100))
    departments.value = sortedDepts
    
    const sortedJobs = [...jobsRes.data].sort((a, b) => (a.display_order || 100) - (b.display_order || 100))
    rawJobTitles.value = sortedJobs
  } catch (e) {
    console.error('Error fetching HR data:', e)
  }
}

const fetchData = async () => {
  isLoading.value = true
  try {
    const meRes = await api.get('/users/me')
    currentUser.value = meRes.data
    await fetchHRData() 
  } catch (e) {
    console.error(e)
    Swal.fire('Error', 'Failed to load data', 'error')
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchData)

// Initial tab placement
watch(currentUser, (newVal) => {
  if (newVal && !props.embedded) {
    activeTab.value = 'users'
  }
}, { immediate: true })
</script>

<style scoped>
/* ─── Color Palette ─────────────────────────────────────
  Dark  : #1a2a3a   Navy
  Mid   : #243447   Hover/Active
  Shade : #2e4057   Borders in dark areas
  Muted : #4a6070   Muted text
  Light : #e8ecef   Light tint
  Pale  : #f2f4f6   Page background
──────────────────────────────────────────────────────── */

/* ═══════════ LAYOUT ═══════════ */
.admin-panel {
  display: flex;
  min-height: 100vh;
  background: #f2f4f6;
  font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
  position: relative;
}

/* ═══════════ SIDEBAR ═══════════ */
.sidebar {
  width: 240px;
  background: #1a2a3a;
  color: #a8bcc8;
  display: flex;
  flex-direction: column;
  padding: 20px 0;
  flex-shrink: 0;
  transition: transform 0.25s ease;
  z-index: 200;
}
.sidebar-logo {
  padding: 0 20px 20px;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #fff;
  border-bottom: 1px solid #2e4057;
  margin-bottom: 12px;
  text-transform: uppercase;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.sidebar-close-btn {
  display: none;
  background: transparent;
  border: none;
  color: #7a9bb0;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
}
.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0 10px;
}
.nav-item {
  background: transparent;
  border: none;
  color: #7a9bb0;
  padding: 11px 14px;
  border-radius: 6px;
  text-align: left;
  cursor: pointer;
  font-size: 0.88rem;
  font-family: inherit;
  transition: all 0.15s;
  font-weight: 500;
}
.nav-item:hover { background: #243447; color: #c8d8e4; }
.nav-item.active { background: #243447; color: #fff; font-weight: 700; border-left: 3px solid #5a8ea8; }
.logout-sidebar-btn {
  margin: 20px 10px 0;
  background: transparent;
  border: 1px solid rgba(231, 76, 60, 0.4);
  color: #e74c3c;
  padding: 10px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.85rem;
  transition: all 0.2s;
  text-align: left;
  font-weight: 600;
}
.logout-sidebar-btn:hover { background: #e74c3c; color: #fff; }

/* Mobile Logout icon */
.mobile-logout-btn {
  background: transparent;
  border: none;
  color: #e74c3c;
  font-size: 1.2rem;
  cursor: pointer;
}

/* Mobile overlay behind sidebar */
.sidebar-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  z-index: 199;
}

/* ═══════════ MOBILE TOPBAR ═══════════ */
.mobile-topbar {
  display: none;
  align-items: center;
  justify-content: space-between;
  background: #1a2a3a;
  color: #fff;
  padding: 12px 16px;
  z-index: 100;
  flex-shrink: 0;
}
.mobile-menu-btn {
  background: transparent;
  border: none;
  color: #a8bcc8;
  font-size: 1.3rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.15s;
  line-height: 1;
}
.mobile-menu-btn:hover { background: #243447; color: #fff; }
.mobile-title {
  font-size: 0.88rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

/* Main Wrapper helps with mobile topbar + scrolling */
.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  height: 100vh;
}

/* ═══════════ MAIN CONTENT ═══════════ */
.admin-content {
  flex: 1;
  padding: 28px;
  overflow-y: auto;
  min-width: 0;
}

/* ═══════════════════════════════════════════════════════
   RESPONSIVE — Tablet + Mobile  (≤ 1024px)
   Sidebar เป็น slide-in drawer สำหรับทุกขนาด ≤ 1024px
═══════════════════════════════════════════════════════ */
@media (max-width: 1024px) {
  .sidebar {
    position: fixed;
    top: 0; left: 0; bottom: 0;
    width: 260px;
    transform: translateX(-100%);
    box-shadow: 4px 0 28px rgba(0,0,0,0.3);
    z-index: 300;
  }
  .sidebar.sidebar-open { transform: translateX(0); }
  .sidebar-close-btn  { display: block; }
  .sidebar-overlay    { display: block; }
  .mobile-topbar      { display: flex; }
  .admin-content      { padding: 20px; }
}
</style>
