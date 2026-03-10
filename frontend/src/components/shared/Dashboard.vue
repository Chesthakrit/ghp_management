<template>
  <div class="dashboard-container">
    <!-- ─── Sidebar ─── -->
    <aside class="sidebar" :class="{ 'sidebar-open': sidebarOpen }">
      <div class="sidebar-logo">
        <span>GHP Platform</span>
        <button class="sidebar-close-btn" @click="sidebarOpen = false">✕</button>
      </div>

      <div class="user-profile-mini">
        <div class="mini-avatar">{{ username?.[0]?.toUpperCase() }}</div>
        <div class="mini-info">
          <span class="mini-name">{{ username }}</span>
          <span v-if="roleName" class="mini-role">{{ roleName }}</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <!-- Dashboard / Projects -->
        <button 
          :class="['nav-item', { active: currentView === 'projects' }]"
          @click="currentView = 'projects'; sidebarOpen = false"
        >
          📊 กิจการทั้งหมด
        </button>

        <!-- Profile -->
        <button 
          :class="['nav-item', { active: currentView === 'profile' }]"
          @click="emit('go-to-profile'); sidebarOpen = false"
        >
          👤 โปรไฟล์ของฉัน
        </button>

        <!-- Admin Features directly in sidebar -->
        <template v-if="canManageUsers || canManageRoles">
          <div class="nav-divider">Admin Features</div>
          
          <button 
            v-if="canManageUsers"
            :class="['nav-item', { active: currentView === 'users' }]"
            @click="currentView = 'users'; sidebarOpen = false"
          >
            👥 การจัดการผู้ใช้
          </button>

          <button 
            v-if="canManageRoles"
            :class="['nav-item', { active: currentView === 'roles' }]"
            @click="currentView = 'roles'; sidebarOpen = false"
          >
            🔐 ตำแหน่งและสิทธิ์
          </button>
        </template>
      </nav>

      <div class="sidebar-footer">
        <button @click="logout" class="btn-logout-sidebar">🚪 Logout</button>
      </div>
    </aside>

    <!-- Overlay for mobile/iPad -->
    <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false"></div>

    <!-- ─── Main Content ─── -->
    <div class="main-wrapper">
      
      <!-- Mobile Topbar -->
      <header class="mobile-topbar">
        <button class="mobile-menu-btn" @click="sidebarOpen = true">☰</button>
        <span class="mobile-title">{{ viewTitle }}</span>
        <div style="width: 40px;"></div> <!-- spacer -->
      </header>

      <main class="dashboard-content">
        
        <!-- View: Projects -->
        <div v-if="currentView === 'projects'">
          <div class="content-header">
            <h2>{{ viewTitle }}</h2>
          </div>

          <!-- Loading State -->
          <div v-if="isLoading" class="loading-spinner">
            Loading...
          </div>

          <!-- Project Grid -->
          <div v-else-if="projects.length > 0" class="projects-grid">
            <div v-for="project in projects" :key="project.id" class="project-card">
              <div class="card-header">
                <h3>{{ project.name }}</h3>
                <span class="status-badge">Active</span>
              </div>
              <div class="card-body">
                <p><strong>Customer:</strong> {{ project.customer }}</p>
                <p><strong>Due Date:</strong> {{ project.due_date || 'N/A' }}</p>
                <p class="description">{{ project.description }}</p>
                <!-- Show Owner ID if Admin (or has permission) -->
                <p v-if="canViewAllProjects" class="owner-info">Owner ID: {{ project.owner_id }}</p>
              </div>
              <div class="card-footer">
                <button class="btn-view">View Details</button>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else class="empty-state">
            <h3>No Projects Found</h3>
            <p>Get started by creating a new project.</p>
          </div>
        </div>

        <!-- View: User Management (Inside Dashboard if needed) -->
        <UserManagement v-if="currentView === 'users'" />
        <RoleManagement v-if="currentView === 'roles'" />

      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'
import Swal from 'sweetalert2'
import UserManagement from '../admin/UserManagement.vue'
import RoleManagement from './RoleManagement.vue'

const emit = defineEmits(['go-to-login', 'go-to-admin', 'go-to-profile'])

const projects = ref([])
const isLoading = ref(false)
const sidebarOpen = ref(false)

// User Info
const username = ref('')
const roleName = ref('')
const permissions = ref([])

// View State
const currentView = ref('users') 

// Permission Checks
const canManageUsers = computed(() => permissions.value.includes('user.manage'))
const canManageRoles = computed(() => permissions.value.includes('role.manage'))
const canViewAllProjects = computed(() => permissions.value.includes('project.view_all'))

const viewTitle = computed(() => {
  const titles = {
    projects: 'กิจการทั้งหมด',
    users: 'การจัดการผู้ใช้',
    roles: 'ตำแหน่งและสิทธิ์'
  }
  return titles[currentView.value] || 'GHP Platform'
})

const fetchProjects = async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    window.location.reload() 
    return
  }
  try {
    isLoading.value = true
    const payload = JSON.parse(atob(token.split('.')[1]))
    username.value = payload.sub
    const userRes = await api.get('/users/me')
    roleName.value = userRes.data.role
    permissions.value = userRes.data.permissions || []
    const response = await api.get('/projects/')
    projects.value = response.data
  } catch (error) {
    console.error('Error fetching data:', error)
    if (error.response && error.response.status === 401) logout()
  } finally {
    isLoading.value = false
  }
}

const logout = () => {
  localStorage.removeItem('token')
  window.location.reload() 
  Swal.fire({ icon: 'success', title: 'Logged Out', timer: 1000, showConfirmButton: false })
}

onMounted(() => { fetchProjects() })
</script>

<style scoped>
.dashboard-container {
  display: flex;
  min-height: 100vh;
  background-color: #f2f4f6;
  font-family: 'Kanit', sans-serif;
  overflow: hidden;
}

/* ═══════════ SIDEBAR ═══════════ */
.sidebar {
  width: 250px;
  background: #1a2a3a;
  color: #fff;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: transform 0.25s ease;
  z-index: 200;
}
.sidebar-logo {
  padding: 24px;
  font-size: 1.1rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.sidebar-close-btn { display: none; background: transparent; border: none; color: #fff; font-size: 1.2rem; cursor: pointer; }

.user-profile-mini {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255,255,255,0.03);
}
.mini-avatar {
  width: 40px; height: 40px;
  background: #3498db;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1.1rem;
}
.mini-info { display: flex; flex-direction: column; }
.mini-name { font-size: 0.9rem; font-weight: 600; }
.mini-role { font-size: 0.72rem; color: #7a9bb0; }

.sidebar-nav {
  flex: 1;
  padding: 16px 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.nav-item {
  background: transparent;
  border: none;
  color: #a8bcc8;
  padding: 12px 14px;
  border-radius: 8px;
  text-align: left;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.88rem;
  transition: all 0.2s;
}
.nav-item:hover { background: rgba(255,255,255,0.05); color: #fff; }
.nav-item.active { background: #3498db; color: #fff; font-weight: 600; }
.nav-divider {
  font-size: 0.65rem;
  color: #576574;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 15px 14px 5px;
  font-weight: 700;
}
.btn-admin-panel-nav { border: 1px dashed rgba(52, 152, 219, 0.4); margin-top: 10px; color: #fff; font-weight: 600; }

.sidebar-footer { padding: 20px; border-top: 1px solid rgba(255,255,255,0.1); }
.btn-logout-sidebar {
  width: 100%;
  padding: 10px;
  background: transparent;
  border: 1px solid rgba(255,255,255,0.2);
  color: #c0a0a0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.btn-logout-sidebar:hover { background: #8b3a3a; color: #fff; border-color: #8b3a3a; }

.sidebar-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 199;
  display: none;
}

/* ═══════════ MAIN CONTENT ═══════════ */
.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.mobile-topbar {
  display: none;
  background: #1a2a3a;
  color: #fff;
  padding: 12px 16px;
  align-items: center;
  justify-content: space-between;
}
.mobile-menu-btn {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 1.4rem;
  cursor: pointer;
}
.mobile-title { font-size: 1rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; }

.dashboard-content {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.content-header h2 { font-size: 1.5rem; color: #1a2a3a; margin: 0; }

/* Project Cards */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}
.project-card {
  background: white; border-radius: 12px; padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.04);
  transition: all 0.25s; border: 1px solid #edf0f2;
}
.project-card:hover { transform: translateY(-4px); box-shadow: 0 12px 20px rgba(0, 0, 0, 0.08); }

.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.card-header h3 { font-size: 1.1rem; color: #1a2a3a; margin: 0; }
.status-badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; background: #f1c40f; color: #fff; font-weight: 600; }
.card-body p { margin: 6px 0; font-size: 0.88rem; color: #576574; }
.description { color: #8395a7; font-size: 0.82rem; margin-top: 8px !important; }
.card-footer { margin-top: 16px; padding-top: 14px; border-top: 1px solid #f2f4f6; display: flex; justify-content: flex-end; }
.btn-view { background: transparent; color: #3498db; border: 1px solid #3498db; padding: 6px 14px; border-radius: 4px; cursor: pointer; transition: all 0.2s; font-size: 0.85rem; }
.btn-view:hover { background: #3498db; color: #fff; }

/* RESPONSIVE */
@media (max-width: 1024px) {
  .mobile-topbar { display: flex; }
  .sidebar-overlay { display: block; }
  .sidebar { position: fixed; top: 0; left: 0; bottom: 0; transform: translateX(-100%); box-shadow: 10px 0 40px rgba(0,0,0,0.3); }
  .sidebar.sidebar-open { transform: translateX(0); }
  .sidebar-close-btn { display: block; }
  .dashboard-content { padding: 20px; }
}
@media (max-width: 640px) {
  .projects-grid { grid-template-columns: 1fr; }
}
.loading-spinner, .empty-state { text-align: center; padding: 60px; color: #a8bcc8; grid-column: 1 / -1; }
.empty-state h3 { color: #1a2a3a; margin-bottom: 6px; }
</style>
