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
        <button v-if="userId" class="admin-panel-btn" @click="$emit('go-back')" style="background-color: #475569; border-color: #475569; color: white;">
          <i class="fas fa-arrow-left"></i> Back to Panel
        </button>
        <button v-else-if="isAdmin" class="admin-panel-btn" @click="$emit('go-to-admin')">
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
            @click="handleMenuClick(item)"
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

          <SkillViewer
            v-else-if="activeMenu === 'skills'"
            :userSkills="userSkills"
            :userEvaluations="autoPercentRatings"
            :overallPercent="overallPercent"
            :subEvaluations="subEvaluations"
            :selectedSkill="selectedSkill"
            :canEvaluate="canEvaluate"
            @select-skill="selectSkill"
            @toggle-sub-duty="toggleSubDuty"
          />

          <AttendancePanel v-else-if="activeMenu === 'attendance'" :userId="userId" />

          <CompanyPolicy v-else-if="activeMenu === 'policy'" />

          <!-- Management Tab for authorized Users/Managers -->
          <div v-else-if="activeMenu === 'manage_users'" class="management-tab">
            <UserManagement 
              @go-to-identity="(id) => $emit('go-to-identity', id)"
              @view-profile="(id) => $emit('view-profile', id)"
              @go-to-register="$emit('go-to-register')"
            />
          </div>

          <!-- Dynamic Rendering of other Admin Modules (using AdminPanel's embedded mode) -->
          <div v-else-if="['manage_hr', 'manage_salary', 'manage_access', 'manage_time_leave', 'manage_attendance_dash'].includes(activeMenu)" class="management-tab-embedded">
            <AdminPanel 
              :embedded="activeMenu.replace('manage_', '')"
              @view-profile="(id) => $emit('view-profile', id)"
              @go-to-identity="(id) => $emit('go-to-identity', id)"
            />
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
import api from '../../api'
import Swal from 'sweetalert2'
import UserManagement from '../shared/UserManagement.vue'
import AdminPanel from '../admin/AdminPanel.vue'
import SkillViewer from './SkillViewer.vue'
import AttendancePanel from './AttendancePanel.vue'
import CompanyPolicy from './CompanyPolicy.vue'

const props = defineProps(['username', 'userId'])
const emit = defineEmits(['go-back', 'logout', 'go-to-identity', 'view-profile', 'go-to-admin'])

const apiBase = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'
const user = ref(null)
const isLoading = ref(false)
const isSidebarOpen = ref(window.innerWidth > 768)
const isMobile = ref(window.innerWidth <= 768)
const activeMenu = ref(props.userId ? 'profile' : (localStorage.getItem('profile_active_menu') || 'profile'))

watch(activeMenu, (n) => {
  if (!props.userId) {
    localStorage.setItem('profile_active_menu', n)
  }
})
const userSkills = ref([])
const userEvaluations = ref({})
const selectedSkill = ref(null)
const subEvaluations = ref({}) // subDutyId -> boolean

// Auto-calculate percentage (0-100) from sub-duty checklist completion
const autoPercentRatings = computed(() => {
  const ratings = {}
  userSkills.value.forEach(skill => {
    const subs = skill.sub_duties || []
    if (subs.length === 0) {
      ratings[skill.id] = 0
      return
    }
    const completed = subs.filter(s => subEvaluations.value[s.id]).length
    ratings[skill.id] = Math.round((completed / subs.length) * 100)
  })
  return ratings
})

// Overall average percentage across all skills
const overallPercent = computed(() => {
  const skillIds = Object.keys(autoPercentRatings.value)
  if (skillIds.length === 0) return 0
  const total = skillIds.reduce((sum, id) => sum + autoPercentRatings.value[id], 0)
  return Math.round(total / skillIds.length)
})

const selectSkill = (skill) => {
  selectedSkill.value = skill
}

const currentUserPermissions = ref(JSON.parse(localStorage.getItem('user_permissions') || '[]'))

const menuItems = computed(() => {
  const perms = currentUserPermissions.value
  
  const baseItems = [
    { id: 'profile', label: 'Personal Card', icon: 'fas fa-user-circle' },
    { id: 'attendance', label: 'Time Recording', icon: 'fas fa-clock' },
    { id: 'skills', label: 'Skill (Tutorial)', icon: 'fas fa-award' },
    { id: 'policy', label: 'Policy & Welfare', icon: 'fas fa-file-contract' },
  ]

  // Add Dynamic Management Tabs based on Permissions
  if (perms.includes('page.usermanagement') || isAdmin.value) {
    baseItems.push({ id: 'manage_users', label: 'Admin (User List)', icon: 'fas fa-users-cog' })
  }
  if (perms.includes('page.hr') || isAdmin.value) {
    baseItems.push({ id: 'manage_hr', label: 'Admin (Section)', icon: 'fas fa-sitemap' })
  }
  if (perms.includes('page.time_leave') || isAdmin.value) {
    baseItems.push({ id: 'manage_time_leave', label: 'Admin (Time)', icon: 'fas fa-hourglass-half' })
  }
  if (perms.includes('page.salary') || isAdmin.value) {
    baseItems.push({ id: 'manage_salary', label: 'Admin (Salary)', icon: 'fas fa-money-check-alt' })
  }
  if (perms.includes('page.access') || isAdmin.value) {
    baseItems.push({ id: 'manage_access', label: 'Admin (Access Control)', icon: 'fas fa-shield-alt' })
  }
  if (perms.includes('page.attendance_dash') || isAdmin.value) {
    baseItems.push({ id: 'manage_attendance_dash', label: 'Admin (Attendance Dash)', icon: 'fas fa-chart-line' })
  }

  return baseItems
})

const handleMenuClick = (item) => {
  activeMenu.value = item.id
  if (isMobile.value) isSidebarOpen.value = false
}

const currentMenuLabel = computed(() => menuItems.value.find(m => m.id === activeMenu.value)?.label)
const currentMenuIcon = computed(() => menuItems.value.find(m => m.id === activeMenu.value)?.icon)

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const isAdmin = computed(() => {
  // Check if LOGGED-IN user is admin (from localStorage)
  const role = (localStorage.getItem('user_role') || '').toLowerCase()
  const uname = (localStorage.getItem('username') || '').toLowerCase()
  return role === 'admin' || uname === 'admin'
})

const hasAdminModulesAccess = computed(() => {
  const perms = currentUserPermissions.value
  return isAdmin.value || perms.some(p => ['page.hr', 'page.salary', 'page.access', 'page.time_leave', 'page.attendance_dash'].includes(p))
})

const canEvaluate = computed(() => {
  if (isAdmin.value) return true
  const perms = currentUserPermissions.value
  return perms.includes('user.manage')
})

const groupedSkills = computed(() => {
  const groups = {}
  userSkills.value.forEach(s => {
    const cat = s.category?.name || 'Uncategorized'
    if (!groups[cat]) groups[cat] = []
    groups[cat].push(s)
  })
  return groups
})

const fetchUserData = async () => {
  isLoading.value = true
  user.value = null
  userSkills.value = []
  userEvaluations.value = {}
  try {
    const targetUserId = props.userId || null
    const endpoint = targetUserId ? `/users/${targetUserId}` : '/users/me'
    const res = await api.get(endpoint)
    user.value = res.data

    // ─── CRITICAL: Refresh current user's permissions in frontend state ───
    if (!props.userId) {
       currentUserPermissions.value = res.data.permissions || []
       localStorage.setItem('user_permissions', JSON.stringify(currentUserPermissions.value))
       localStorage.setItem('user_role', res.data.role || '')
    }

    let evalsRes = { data: [] }
    let subEvalsRes = { data: [] }
    let jobsRes = { data: [] }
    let deptsRes = { data: [] }
    
    try {
      const [eRes, seRes, jRes, dRes] = await Promise.all([
        api.get(`/hr/evaluations/${user.value.id}`),
        api.get(`/hr/sub-evaluations/${user.value.id}`),
        api.get('/hr/job-titles'),
        api.get('/hr/departments')
      ])
      evalsRes = eRes
      subEvalsRes = seRes
      jobsRes = jRes
      deptsRes = dRes
    } catch (e) {
      console.warn('Individual HR data fetch failed, attempting partial load', e)
    }

    // 1. Process Evaluations
    const evMap = {}
    if (evalsRes.data) {
      evalsRes.data.forEach(ev => {
        evMap[ev.duty_id] = ev.score
      })
    }
    userEvaluations.value = evMap

    // 1.1 Process Sub Evaluations
    const subMap = {}
    if (subEvalsRes.data) {
      subEvalsRes.data.forEach(sev => {
        subMap[sev.sub_duty_id] = sev.is_completed
      })
    }
    subEvaluations.value = subMap

    // 2. Process Skills for this user's Job Title
    const userJT = (user.value.employee_profile?.job_title || '').trim().toLowerCase()
    const userDeptSlug = (user.value.employee_profile?.department || '').trim().toLowerCase()
    
    if (userJT && jobsRes.data) {
      // Find the department ID first to disambiguate
      const matchedDept = deptsRes.data?.find(d => d.value.trim().toLowerCase() === userDeptSlug)
      
      const matchedJob = jobsRes.data.find(j => {
        const nameMatch = (j.name || '').trim().toLowerCase() === userJT
        if (matchedDept) {
          return nameMatch && j.department_id === matchedDept.id
        }
        return nameMatch
      })

      if (matchedJob) {
        userSkills.value = matchedJob.duties || []
        console.log(`Matched Job Title: ${matchedJob.name}`, userSkills.value)
      } else {
        console.warn(`No match found for job title: "${userJT}" in department: "${userDeptSlug}"`)
      }
    }

  } catch (err) {
    console.error('Error fetching user profile:', err)
  } finally {
    isLoading.value = false
  }
}

const toggleSubDuty = async (subId) => {
  const newState = !subEvaluations.value[subId]
  try {
    await api.post('/hr/sub-evaluations', {
      user_id: user.value.id,
      sub_duty_id: subId,
      is_completed: newState
    })
    subEvaluations.value[subId] = newState
  } catch (err) {
    Swal.fire('Error', 'Failed to update checklist', 'error')
  }
}

const getStarClass = (skillId, starIndex) => {
  const score = userEvaluations.value[skillId] || 0
  if (starIndex <= score) return 'fas fa-star text-gold'
  return 'far fa-star text-muted'
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
@import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600&family=Outfit:wght@300;400;500;600;700&display=swap');

.user-profile-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f1f5f9;
  font-family: 'Outfit', 'Kanit', sans-serif;
  color: #1e293b;
}

/* ─── Header ─── */
.profile-header {
  height: 64px;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  color: #f8fafc;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  z-index: 55;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
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
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 8px;
  font-weight: 800;
  font-size: 1.1rem;
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
  letter-spacing: 0.05em;
}

.brand-name {
  font-weight: 700;
  font-size: 0.9rem;
  letter-spacing: 0.15em;
  color: #f1f5f9;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
.header-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.admin-panel-btn {
  background: rgba(30, 41, 59, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
  padding: 8px 16px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.admin-panel-btn:hover {
  background: #3b82f6;
  color: #fff;
  border-color: #3b82f6;
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
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
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: left;
  font-family: 'Outfit', 'Kanit', sans-serif;
  font-weight: 500;
  font-size: 0.95rem;
}

.nav-item i {
  width: 24px;
  font-size: 1.25rem;
  text-align: center;
  transition: transform 0.2s;
}

.nav-item:hover i {
  transform: scale(1.15);
  color: #3b82f6;
}

.nav-item.active i {
  color: #fff;
  filter: drop-shadow(0 0 4px rgba(255, 255, 255, 0.4));
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

/* ─── Skills Tab Styles ─── */
.skills-content {
  animation: fadeIn 0.3s ease;
}

.section-card-flat {
  background: #fff;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.category-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #3b82f6;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 20px 0 12px 0;
  padding-left: 10px;
  border-left: 3px solid #3b82f6;
}

.skill-items-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skill-item-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8fafc;
  border-radius: 12px;
  transition: transform 0.2s;
}

.skill-item-row:hover {
  transform: translateX(4px);
  background: #f1f5f9;
}

.skill-info-box {
  flex: 1;
}

.skill-name-text {
  font-weight: 600;
  color: #1e293b;
  font-size: 1rem;
}

.skill-info-popup-btn {
  font-size: 0.8rem;
  color: #3b82f6;
  margin-right: 10px;
  cursor: pointer;
  opacity: 0.5;
  transition: all 0.2s;
  background: #eff6ff;
  border: 1px solid #dbeafe;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.skill-info-popup-btn:hover {
  opacity: 1;
  transform: scale(1.2);
}

.skill-rating-box {
  text-align: right;
  min-width: 160px;
}

.stars-row {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  font-size: 1.15rem;
  margin-bottom: 4px;
}

.stars-row i {
  margin-left: 2px;
}

.text-gold { color: #f59e0b; }
.text-muted { color: #cbd5e0; }

.clickable {
  cursor: pointer;
  transition: transform 0.15s;
}

.clickable:hover {
  transform: scale(1.2);
}

.rating-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
}

.no-skills-notice {
  text-align: center;
  padding: 40px;
  color: #94a3b8;
}

.no-skills-notice i {
  font-size: 2rem;
  margin-bottom: 12px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ─── Skills Tab Split View ─── */
.skills-view-wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: flex-start;
  animation: fadeIn 0.3s ease;
}

@media (max-width: 1200px) {
  .skills-view-wrapper {
    grid-template-columns: 1fr;
  }
}

.skills-list-side {
  display: flex;
  flex-direction: column;
}

.no-shadow { box-shadow: none !important; }

.skill-info-btn-inline {
  font-size: 0.8rem;
  color: #3b82f6;
  margin-right: 10px;
  cursor: pointer;
  opacity: 0.4;
  transition: all 0.2s;
  background: #eff6ff;
  border: 1px solid #dbeafe;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.skill-info-btn-inline:hover, .skill-info-btn-inline.active {
  opacity: 1;
  background: #3b82f6;
  color: #fff;
}

.skill-item-row.active-selection {
  border: 2px solid #3b82f6;
  background: #fff;
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}
</style>
