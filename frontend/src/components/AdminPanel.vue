<template>
  <div class="admin-panel">

    <!-- ─── Sidebar (Desktop / iPad) ─── -->
    <aside class="sidebar" :class="{ 'sidebar-open': sidebarOpen }">
      <div class="sidebar-logo">
        <span>Admin Panel</span>
        <!-- Mobile: close X -->
        <button class="sidebar-close-btn" @click="sidebarOpen = false">✕</button>
      </div>
      <nav class="sidebar-nav">
        <button
          :class="['nav-item', { active: activeTab === 'users' }]"
          @click="activeTab = 'users'; sidebarOpen = false"
        >👥 User Management</button>
        <button
          :class="['nav-item', { active: activeTab === 'roles' }]"
          @click="activeTab = 'roles'; sidebarOpen = false"
        >🔐 Roles & Permissions</button>
      </nav>
      <button class="back-btn" @click="$emit('go-back')">
        ← Back to Dashboard
      </button>
    </aside>

    <!-- Mobile Overlay -->
    <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false"></div>

    <!-- ─── Main Content ─── -->
    <main class="admin-content">

      <!-- Mobile Top Bar -->
      <div class="mobile-topbar">
        <button class="mobile-menu-btn" @click="sidebarOpen = true">☰</button>
        <span class="mobile-title">{{ activeTab === 'users' ? 'User Management' : 'Roles & Permissions' }}</span>
        <button class="mobile-back-btn" @click="$emit('go-back')">✕</button>
      </div>

      <!-- TAB: Users -->
      <div v-if="activeTab === 'users'">
        <!-- Stats Overview -->
        <div class="stats-row">
          <div class="stat-card">
            <div class="stat-number">{{ users.length }}</div>
            <div class="stat-label">ทั้งหมด</div>
          </div>
          <div class="stat-card" v-for="dept in departmentStats" :key="dept.name">
            <div class="stat-number">{{ dept.count }}</div>
            <div class="stat-label">{{ deptLabel(dept.name) }}</div>
          </div>
        </div>

        <!-- User Table -->
        <div class="section-card">
          <div class="section-header">
            <h2>Employee List</h2>
            <div class="controls-row">
              <div class="search-row">
                <input v-model="searchQuery" placeholder="Search..." class="search-input" />
                <select v-model="filterDept" class="filter-select">
                  <option value="">All Dept.</option>
                  <option v-for="d in departments" :key="d.value" :value="d.value">{{ d.label }}</option>
                </select>
              </div>
              <!-- Sort Controls -->
              <div class="sort-row">
                <span class="sort-label">Sort:</span>
                <button
                  :class="['sort-btn', { active: sortBy === 'dept' }]"
                  @click="toggleSort('dept')"
                >
                  Department
                  <span v-if="sortBy === 'dept'" class="sort-arrow">{{ sortDir === 'asc' ? '↑' : '↓' }}</span>
                </button>
                <button
                  :class="['sort-btn', { active: sortBy === 'hire_date' }]"
                  @click="toggleSort('hire_date')"
                >
                  Hire Date
                  <span v-if="sortBy === 'hire_date'" class="sort-arrow">{{ sortDir === 'asc' ? '↑' : '↓' }}</span>
                </button>
                <button v-if="sortBy" class="sort-btn clear" @click="sortBy = ''; sortDir = 'asc'">× Clear</button>
              </div>
            </div>
          </div>

          <div v-if="isLoading" class="loading">Loading...</div>

          <!-- ─── Desktop / iPad Table ─── -->
          <div v-else class="table-wrapper">
            <table class="user-table">
              <thead>
                <tr>
                  <th>Full Name</th>
                  <th class="hide-tablet">Username</th>
                  <th
                    class="hide-mobile sortable-th"
                    :class="{ sorted: sortBy === 'dept' }"
                    @click="toggleSort('dept')"
                  >
                    Department
                    <span class="th-arrow">{{ sortBy === 'dept' ? (sortDir === 'asc' ? '↑' : '↓') : '⇅' }}</span>
                  </th>
                  <th class="hide-mobile">Job Title</th>
                  <th class="hide-mobile">Role</th>
                  <th class="hide-tablet">Status</th>
                  <th
                    class="hide-tablet sortable-th"
                    :class="{ sorted: sortBy === 'hire_date' }"
                    @click="toggleSort('hire_date')"
                  >
                    Hire Date
                    <span class="th-arrow">{{ sortBy === 'hire_date' ? (sortDir === 'asc' ? '↑' : '↓') : '⇅' }}</span>
                  </th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in filteredUsers" :key="user.id">
                  <td>
                    <div class="name-cell">
                      <div class="avatar" :class="{ 'has-photo': user.photo_path }" @click="user.photo_path && openPhoto(`${apiBase}/${user.photo_path}`)">
                        <img v-if="user.photo_path" :src="`${apiBase}/${user.photo_path}`" class="avatar-img" :alt="getInitials(user)" />
                        <span v-else>{{ getInitials(user) }}</span>
                      </div>
                      <div class="name-info">
                        <span class="name-text">{{ user.first_name || '-' }} {{ user.last_name || '' }}</span>
                        <span v-if="user.nickname" class="nickname-text">({{ user.nickname }})</span>
                        <!-- Show on mobile only -->
                        <span class="show-mobile job-title-sub">{{ user.employee_profile?.job_title || '' }}</span>
                        <span class="show-mobile">
                          <span v-if="user.employee_profile?.department" class="dept-badge sm">{{ deptLabel(user.employee_profile.department) }}</span>
                        </span>
                      </div>
                    </div>
                  </td>
                  <td class="hide-tablet username-cell">{{ user.username }}</td>
                  <td class="hide-mobile">
                    <span v-if="user.employee_profile?.department" class="dept-badge">{{ deptLabel(user.employee_profile.department) }}</span>
                    <span v-else class="no-data">—</span>
                  </td>
                  <td class="hide-mobile">{{ user.employee_profile?.job_title || '—' }}</td>
                  <td class="hide-mobile">
                    <span class="role-badge">{{ user.role }}</span>
                  </td>
                  <td class="hide-tablet">
                    <span :class="['emp-status-badge', user.employee_profile?.employment_status || 'intern']">
                      {{ empStatusLabel(user.employee_profile?.employment_status) }}
                    </span>
                  </td>
                  <td class="hide-tablet date-cell">{{ fmtDate(user.employee_profile?.hire_date) }}</td>
                  <td class="action-cell">
                    <template v-if="user.role !== 'admin'">
                      <button class="btn-id-card" @click="openEditIdentity(user)" title="Identity">🪪</button>
                      <button class="btn-edit" @click="openEdit(user)" title="Edit">✏️</button>
                      <button class="btn-delete" @click="deleteUser(user)" title="Delete">🗑️</button>
                    </template>
                    <span v-else class="admin-lock-badge">Admin</span>
                  </td>
                </tr>
                <tr v-if="filteredUsers.length === 0">
                  <td colspan="8" class="empty-row">No records found</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- TAB: Roles -->
      <div v-if="activeTab === 'roles'">
        <RoleManagement />
      </div>

    </main>

    <!-- ─── Edit User Modal ─── -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-box">
        <h3>Edit Employee</h3>
        <div class="modal-user-info">
          <div class="avatar large">
            <img v-if="editingUser?.photo_path" :src="`${apiBase}/${editingUser.photo_path}`" class="avatar-img" />
            <span v-else>{{ getInitials(editingUser) }}</span>
          </div>
          <div>
            <strong>{{ editingUser?.first_name || editingUser?.username }} {{ editingUser?.last_name || '' }}</strong>
            <span v-if="editingUser?.nickname" class="nickname-text">({{ editingUser.nickname }})</span>
            <span>{{ editingUser?.username }}</span>
          </div>
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label>Department</label>
            <select v-model="form.department" class="form-input">
              <option value="">— Not specified —</option>
              <option v-for="d in departments" :key="d.value" :value="d.value">{{ d.label }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Job Title</label>
            <select v-model="form.job_title" class="form-input" :disabled="!form.department">
              <option value="">{{ form.department ? '— Select Job Title —' : '— Select Department first —' }}</option>
              <option v-for="t in (jobTitlesByDept[form.department] || [])" :key="t" :value="t">{{ t }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>System Role</label>
            <select v-model="form.role" class="form-input" :disabled="isAdminUser">
              <option v-for="role in availableRoles" :key="role.id" :value="role.name">{{ role.name }}</option>
            </select>
            <small v-if="isAdminUser" class="lock-hint">Master Admin role cannot be changed</small>
          </div>
          <div class="form-group">
            <label>Employment Status</label>
            <select v-model="form.employment_status" class="form-input">
              <option value="intern">Intern</option>
              <option value="permanent">Permanent</option>
              <option value="terminated">Terminated</option>
            </select>
          </div>
          <div class="form-group" v-if="editingUser?.employee_profile?.termination_date">
            <label>Termination Date</label>
            <input :value="editingUser.employee_profile.termination_date" type="date" class="form-input" disabled />
            <small class="lock-hint">Set automatically when status changes to Terminated</small>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-cancel" @click="closeModal">Cancel</button>
          <button class="btn-save" @click="saveUser" :disabled="isSaving">
            {{ isSaving ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </div>
    </div>

  </div>

  <!-- Photo Popup -->
  <div v-if="photoPopup" class="photo-popup-overlay" @click.self="closePhoto">
    <div class="photo-popup-box">
      <img :src="photoPopup" class="popup-img" />
      <button class="popup-close" @click="closePhoto">&times;</button>
    </div>
  </div>

</template>


<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import api from '../api'
import Swal from 'sweetalert2'
import RoleManagement from './RoleManagement.vue'

const apiBase = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

const emit = defineEmits(['go-back', 'go-to-identity'])

const activeTab = ref('users')
const sidebarOpen = ref(false)
const users = ref([])
const roles = ref([])
const isLoading = ref(false)
const isSaving = ref(false)
const searchQuery  = ref('')
const filterDept   = ref('')
const sortBy       = ref('')       // 'dept' | 'hire_date' | ''
const sortDir      = ref('asc')    // 'asc' | 'desc'
const showModal = ref(false)
const editingUser = ref(null)
const photoPopup = ref(null)

const openPhoto  = (url) => { photoPopup.value = url }
const closePhoto = ()    => { photoPopup.value = null }

const departments = [
  { value: 'office',       label: 'Office' },
  { value: 'draftman',    label: 'Draftman' },
  { value: 'production',  label: 'Production' },
  { value: 'installation',label: 'Installation' },
  { value: 'management',  label: 'Management' },
]

const jobTitlesByDept = {
  office:       ['Admin', 'Accounting', 'Purchasing', 'Manager', 'Supervisor'],
  draftman:     ['Master Draftman', 'Senior Draftman', 'Junior Draftman'],
  production:   ['QC', 'CNC-Edge', 'Custom', 'Packing'],
  installation: ['Supervisor', 'Installer', 'Assistant'],
  management:   ['CEO'],
}

const form = ref({
  first_name: '',
  last_name: '',
  department: '',
  job_title: '',
  role: '',
  is_active: true,
  hire_date: '',
  employment_status: 'intern',
})

// Reset job_title when department changes
watch(() => form.value.department, () => {
  form.value.job_title = ''
})


const deptLabel = (val) => departments.find(d => d.value === val)?.label || val || '—'

// แปลง YYYY-MM-DD → DD/MM/YYYY (คส.) — คืน '—' ถ้าไม่มีค่า
const fmtDate = (iso) => {
  if (!iso) return '—'
  const [y, m, d] = iso.split('-')
  if (!y || !m || !d) return iso
  return `${d}/${m}/${y}`
}

const empStatusLabel = (val) => {
  const map = { intern: 'Intern', permanent: 'Permanent', terminated: 'Terminated' }
  return map[val] || '—'
}

const getInitials = (user) => {
  if (!user) return '?'
  const f = user.first_name?.[0] || user.username?.[0] || '?'
  const l = user.last_name?.[0] || ''
  return (f + l).toUpperCase()
}

const departmentStats = computed(() => {
  const counts = {}
  for (const u of users.value) {
    const dept = u.employee_profile?.department
    if (dept) counts[dept] = (counts[dept] || 0) + 1
  }
  return Object.entries(counts).map(([name, count]) => ({ name, count }))
})

const filteredUsers = computed(() => {
  let list = users.value.filter(u => {
    const q = searchQuery.value.toLowerCase()
    const matchSearch = !q ||
      u.username.toLowerCase().includes(q) ||
      (u.first_name || '').toLowerCase().includes(q) ||
      (u.last_name || '').toLowerCase().includes(q)
    const matchDept = !filterDept.value || u.employee_profile?.department === filterDept.value
    return matchSearch && matchDept
  })

  // Sorting
  if (sortBy.value === 'dept') {
    list = [...list].sort((a, b) => {
      const da = a.employee_profile?.department || ''
      const db = b.employee_profile?.department || ''
      return sortDir.value === 'asc' ? da.localeCompare(db) : db.localeCompare(da)
    })
  } else if (sortBy.value === 'hire_date') {
    list = [...list].sort((a, b) => {
      const da = a.employee_profile?.hire_date || ''
      const db = b.employee_profile?.hire_date || ''
      if (!da && !db) return 0
      if (!da) return 1
      if (!db) return -1
      return sortDir.value === 'asc'
        ? da.localeCompare(db)
        : db.localeCompare(da)
    })
  }

  return list
})

// Toggle sort: คลิกซ้ำที่ column เดิม → สลับ asc/desc; column ใหม่ → เริ่มต้น asc
const toggleSort = (field) => {
  if (sortBy.value === field) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value  = field
    sortDir.value = 'asc'
  }
}

// ตรวจว่ากำลังแก้ไข admin user หรือไม่
const isAdminUser = computed(() => editingUser.value?.role === 'admin')

// Role options: ถ้าแก้ไข admin → แสดง admin ด้วย, ถ้าไม่ใช่ → ซ่อน admin
const availableRoles = computed(() => {
  if (isAdminUser.value) return roles.value
  return roles.value.filter(r => r.name !== 'admin')
})

const fetchData = async () => {
  isLoading.value = true
  const token = localStorage.getItem('token')
  try {
    const [usersRes, rolesRes] = await Promise.all([
      api.get('/users/'),
      api.get('/roles/'),
    ])
    users.value = usersRes.data
    roles.value = rolesRes.data
  } catch (e) {
    console.error(e)
    Swal.fire('Error', 'Failed to load data', 'error')
  } finally {
    isLoading.value = false
  }
}

const openEdit = (user) => {
  editingUser.value = user
  form.value = {
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    department: user.employee_profile?.department || '',
    job_title: user.employee_profile?.job_title || '',
    role: user.role || '',
    is_active: user.is_active,
    hire_date: user.employee_profile?.hire_date || '',
    employment_status: user.employee_profile?.employment_status || 'intern',
  }
  showModal.value = true
}

const openEditIdentity = (user) => {
  emit('go-to-identity', user.id)
}

const closeModal = () => {
  showModal.value = false
  editingUser.value = null
}

const saveUser = async () => {
  isSaving.value = true
  const token = localStorage.getItem('token')
  try {
    // 1. อัปเดตข้อมูลส่วนตัว + Role
    const userRes = await api.put(
      `/users/${editingUser.value.id}`,
      {
        role: form.value.role,
        is_active: form.value.is_active,
        first_name: form.value.first_name,
        last_name: form.value.last_name,
      }
    )

    // 2. อัปเดตข้อมูลบริษัท (EmployeeProfile)
    const profileRes = await api.put(
      `/users/${editingUser.value.id}/profile`,
      {
        department: form.value.department,
        job_title: form.value.job_title,
        hire_date: form.value.hire_date,
        employment_status: form.value.employment_status,
      }
    )

    // Update local list
    const idx = users.value.findIndex(u => u.id === editingUser.value.id)
    if (idx !== -1) users.value[idx] = profileRes.data

    Swal.fire({ icon: 'success', title: 'Saved!', timer: 1200, showConfirmButton: false })
    closeModal()
  } catch (e) {
    console.error(e)
    Swal.fire('Error', e.response?.data?.detail || 'Save failed', 'error')
  } finally {
    isSaving.value = false
  }
}

const deleteUser = async (user) => {
  const result = await Swal.fire({
    title: 'Delete Employee?',
    html: `<b>${user.first_name || user.username} ${user.last_name || ''}</b> will be permanently removed.`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    confirmButtonColor: '#1a2a3a',
    reverseButtons: true,
  })
  if (!result.isConfirmed) return

  const token = localStorage.getItem('token')
  try {
    await api.delete(`/users/${user.id}`)
    users.value = users.value.filter(u => u.id !== user.id)
    Swal.fire({ icon: 'success', title: 'Deleted', timer: 1000, showConfirmButton: false })
  } catch (e) {
    Swal.fire('Error', e.response?.data?.detail || 'Delete failed', 'error')
  }
}

onMounted(fetchData)
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
  width: 220px;
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
.back-btn {
  margin: 20px 10px 0;
  background: transparent;
  border: 1px solid #2e4057;
  color: #7a9bb0;
  padding: 9px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.85rem;
  transition: all 0.15s;
  text-align: left;
}
.back-btn:hover { background: #243447; color: #c8d8e4; }

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
  margin: -16px -16px 16px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.mobile-menu-btn, .mobile-back-btn {
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
.mobile-menu-btn:hover, .mobile-back-btn:hover { background: #243447; color: #fff; }
.mobile-title {
  font-size: 0.88rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

/* ═══════════ MAIN CONTENT ═══════════ */
.admin-content {
  flex: 1;
  padding: 28px;
  overflow-y: auto;
  min-width: 0;
}

/* ═══════════ STATS ═══════════ */
.stats-row {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.stat-card {
  background: white;
  border-radius: 8px;
  padding: 14px 20px;
  border: 1px solid #dde3e8;
  min-width: 90px;
  text-align: center;
  flex: 1;
}
.stat-number { font-size: 1.7rem; font-weight: 700; color: #1a2a3a; }
.stat-label  { font-size: 0.74rem; color: #7a9bb0; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }

/* ═══════════ SECTION CARD ═══════════ */
.section-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #dde3e8;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 10px;
}
.section-header h2 { margin: 0; font-size: 0.9rem; font-weight: 700; color: #1a2a3a; letter-spacing: 0.04em; text-transform: uppercase; }
.search-row { display: flex; gap: 8px; flex-wrap: wrap; }
.search-input, .filter-select {
  padding: 8px 12px;
  border: 1px solid #ccd6de;
  border-radius: 6px;
  font-family: inherit;
  font-size: 0.88rem;
  background: #f7f9fa;
  color: #1a2a3a;
}
.search-input:focus, .filter-select:focus { outline: none; border-color: #4a6070; background: white; }
.search-input { width: 200px; }

/* ═══════════ SORT CONTROLS ═══════════ */
.controls-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
}
.sort-row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.sort-label {
  font-size: 0.72rem;
  color: #7a9bb0;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.sort-btn {
  padding: 5px 11px;
  border: 1px solid #ccd6de;
  border-radius: 20px;
  background: #f7f9fa;
  color: #4a6070;
  font-size: 0.78rem;
  font-family: inherit;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 4px;
}
.sort-btn:hover { background: #e8ecef; border-color: #4a6070; color: #1a2a3a; }
.sort-btn.active {
  background: #1a2a3a;
  border-color: #1a2a3a;
  color: #c8d8e4;
  font-weight: 700;
}
.sort-btn.clear { border-color: #c0a0a0; color: #8b3a3a; background: transparent; }
.sort-btn.clear:hover { background: #8b3a3a; color: #fff; border-color: #8b3a3a; }
.sort-arrow { font-size: 0.85rem; font-weight: 700; }

/* Sortable table headers */
.sortable-th {
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}
.sortable-th:hover { background: #e8ecef !important; color: #1a2a3a; }
.sortable-th.sorted { background: #dde3e8 !important; color: #1a2a3a; }
.th-arrow { margin-left: 4px; font-size: 0.8rem; color: #7a9bb0; }
.sortable-th.sorted .th-arrow { color: #1a2a3a; font-weight: 700; }

/* ═══════════ TABLE ═══════════ */
.table-wrapper { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.user-table { width: 100%; border-collapse: collapse; min-width: 360px; }
.user-table th {
  text-align: left;
  padding: 9px 12px;
  background: #f2f4f6;
  font-size: 0.72rem;
  color: #4a6070;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  border-bottom: 1px solid #dde3e8;
  white-space: nowrap;
}
.user-table td { padding: 11px 12px; border-bottom: 1px solid #edf0f2; vertical-align: middle; font-size: 0.87rem; color: #2c3e50; }
.user-table tr:hover td { background: #f7f9fa; }

/* Responsive column helpers */
.hide-mobile  {} /* visible by default; hidden on mobile */
.hide-tablet  {} /* visible by default; hidden on tablet+mobile */
.show-mobile  { display: none; } /* hidden by default; shown only on mobile */

/* Name cell */
.name-cell { display: flex; align-items: center; gap: 10px; }
.avatar {
  width: 40px; height: 40px;
  border-radius: 50%;
  background: #1a2a3a;
  color: #a8bcc8;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.76rem; font-weight: 700;
  flex-shrink: 0;
  overflow: hidden;
  transition: box-shadow 0.15s;
}
.avatar.has-photo { cursor: pointer; }
.avatar.has-photo:hover { box-shadow: 0 0 0 2px #2e4057, 0 0 0 4px #a8bcc8; }
.avatar.large { width: 50px; height: 50px; font-size: 0.88rem; }
.avatar-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }

.name-info { display: flex; flex-direction: column; gap: 2px; }
.name-text  { font-size: 0.87rem; color: #1a2a3a; font-weight: 500; }
.nickname-text { font-size: 0.74rem; color: #7a9bb0; }
.username-sub  { font-size: 0.73rem; color: #7a9bb0; }
.job-title-sub { font-size: 0.73rem; color: #4a6070; font-style: italic; }
.username-cell { color: #7a9bb0; font-size: 0.83rem; }
.no-data { color: #b0c4d0; }

/* Badges */
.dept-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.72rem;
  font-weight: 600;
  background: #e8ecef;
  color: #2e4057;
  border: 1px solid #ccd6de;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
}
.dept-badge.sm { font-size: 0.66rem; padding: 2px 6px; }

.emp-status-badge { padding: 3px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; white-space: nowrap; }
.emp-status-badge.intern    { background: #e8ecef; color: #4a6070; border: 1px solid #ccd6de; }
.emp-status-badge.permanent { background: #2e4057; color: #c8d8e4; border: 1px solid #2e4057; }
.emp-status-badge.terminated{ background: #1a2a3a; color: #7a9bb0; border: 1px solid #1a2a3a; }

.date-cell { font-size: 0.82rem; color: #7a9bb0; white-space: nowrap; }

.role-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.72rem;
  font-weight: 700;
  background: #e8ecef;
  color: #1a2a3a;
  border: 1px solid #ccd6de;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

/* Action buttons (emoji+icon style) */
.action-cell { display: flex; gap: 4px; align-items: center; }
.btn-edit, .btn-id-card {
  background: #1a2a3a; color: #a8bcc8;
  border: none; padding: 7px 9px;
  border-radius: 5px; cursor: pointer;
  font-size: 1rem; line-height: 1;
  transition: background 0.15s;
}
.btn-edit:hover, .btn-id-card:hover { background: #243447; color: #fff; }
.btn-delete {
  background: transparent; color: #8b3a3a;
  border: 1px solid #c0a0a0; padding: 7px 9px;
  border-radius: 5px; cursor: pointer;
  font-size: 1rem; line-height: 1;
  transition: all 0.15s;
}
.btn-delete:hover { background: #8b3a3a; color: #fff; border-color: #8b3a3a; }

.admin-lock-badge {
  background: #f2f4f6;
  color: #7a9bb0;
  border: 1px solid #ccd6de;
  padding: 4px 8px;
  border-radius: 5px;
  font-size: 0.7rem;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.lock-hint  { color: #7a9bb0; font-size: 0.74rem; margin-top: 4px; }
.empty-row  { text-align: center; color: #b0c4d0; padding: 40px !important; font-size: 0.88rem; }
.loading    { text-align: center; padding: 40px; color: #7a9bb0; font-size: 0.88rem; }

/* ═══════════ MODAL ═══════════ */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(26,42,58,0.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
  padding: 16px;
}
.modal-box {
  background: white;
  border-radius: 10px;
  padding: 24px;
  width: 100%; max-width: 540px;
  max-height: 90vh; overflow-y: auto;
  border: 1px solid #dde3e8;
}
.modal-box h3 { margin: 0 0 14px; font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; color: #1a2a3a; }
.modal-user-info {
  display: flex; align-items: center; gap: 12px;
  padding: 10px; background: #f2f4f6;
  border-radius: 7px; margin-bottom: 18px;
  border: 1px solid #dde3e8;
}
.modal-user-info strong { display: block; color: #1a2a3a; font-size: 0.92rem; }
.modal-user-info span   { font-size: 0.8rem; color: #7a9bb0; }
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}
.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-group label { font-size: 0.73rem; color: #4a6070; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }
.form-input {
  padding: 9px 10px;
  border: 1px solid #ccd6de; border-radius: 6px;
  font-family: inherit; font-size: 0.88rem;
  background: #f7f9fa; color: #1a2a3a;
  width: 100%; box-sizing: border-box;
}
.form-input:focus    { outline: none; border-color: #2e4057; background: white; }
.form-input:disabled { background: #edf0f2; color: #7a9bb0; cursor: not-allowed; }
.modal-actions {
  display: flex; justify-content: flex-end; gap: 8px;
  margin-top: 20px; padding-top: 14px;
  border-top: 1px solid #edf0f2;
}
.btn-cancel {
  background: #f2f4f6; border: 1px solid #ccd6de; padding: 9px 18px;
  border-radius: 6px; cursor: pointer;
  font-family: inherit; font-size: 0.88rem; color: #4a6070;
  transition: background 0.15s;
}
.btn-cancel:hover { background: #e8ecef; }
.btn-save {
  background: #1a2a3a; color: #a8bcc8; border: none;
  padding: 9px 22px; border-radius: 6px; cursor: pointer;
  font-family: inherit; font-weight: 700; font-size: 0.88rem;
  letter-spacing: 0.03em; transition: background 0.15s;
}
.btn-save:hover:not(:disabled) { background: #243447; color: #fff; }
.btn-save:disabled { opacity: 0.4; cursor: not-allowed; }

/* ═══════════ PHOTO POPUP ═══════════ */
.photo-popup-overlay {
  position: fixed; inset: 0;
  background: rgba(26,42,58,0.65);
  backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  z-index: 2000;
}
.photo-popup-box {
  position: relative;
  background: white;
  border-radius: 10px;
  padding: 8px;
  box-shadow: 0 20px 60px rgba(26,42,58,0.4);
  max-width: 320px; width: 90vw;
}
.popup-img { width: 100%; border-radius: 6px; display: block; }
.popup-close {
  position: absolute; top: -10px; right: -10px;
  width: 28px; height: 28px; border-radius: 50%;
  background: #1a2a3a; color: #a8bcc8;
  border: none; font-size: 1.1rem; line-height: 1;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: background 0.15s;
}
.popup-close:hover { background: #243447; color: #fff; }

/* ═══════════════════════════════════════════════════════
   RESPONSIVE — Tablet + Mobile  (≤ 1024px)
   Sidebar เป็น slide-in drawer สำหรับทุกขนาด ≤ 1024px
═══════════════════════════════════════════════════════ */
@media (max-width: 1024px) {

  /* --- Sidebar: slide-in drawer --- */
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

  /* --- Show topbar (hamburger + title + back) --- */
  .mobile-topbar { display: flex; }

  /* --- Main content full width --- */
  .admin-content { padding: 20px; }

  /* --- Stats flexible --- */
  .stats-row { flex-wrap: wrap; gap: 10px; }
  .stat-card { padding: 12px 16px; flex: 1; min-width: 80px; }
  .stat-number { font-size: 1.5rem; }

  /* --- Hide lower-priority table columns on tablet --- */
  .hide-tablet { display: none !important; }
  .search-input { width: 160px; }
}

/* ═══════════════════════════════════════════
   RESPONSIVE — Mobile only  (≤ 640px)
   เพิ่มเติมจาก tablet: ซ่อน column มากขึ้น,
   modal เป็น bottom sheet, table compact
═══════════════════════════════════════════ */
@media (max-width: 640px) {

  /* Drawer narrower on small phone */
  .sidebar { width: 265px; }

  /* Tighter padding */
  .admin-content { padding: 16px; }

  /* --- Stats: 2-per-row grid --- */
  .stats-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 14px; }
  .stat-card { padding: 10px 12px; min-width: 0; }
  .stat-number { font-size: 1.3rem; }
  .stat-label  { font-size: 0.64rem; }

  /* Section card */
  .section-card { padding: 12px; }
  .section-header { flex-direction: column; align-items: flex-start; gap: 8px; margin-bottom: 12px; }
  .section-header h2 { font-size: 0.82rem; }

  /* Search full width */
  .search-row { width: 100%; }
  .search-input { flex: 1; min-width: 0; width: auto; }
  .filter-select { flex: 0 0 auto; font-size: 0.82rem; padding: 7px 8px; }

  /* Sort controls full width */
  .controls-row { align-items: flex-start; width: 100%; }
  .sort-row { width: 100%; }
  .sort-btn { font-size: 0.74rem; padding: 5px 10px; }

  /* Hide more columns on mobile */
  .hide-mobile { display: none !important; }

  /* Show inline mobile data */
  .show-mobile { display: block !important; }

  /* Table compact */
  .user-table td { padding: 9px 8px; font-size: 0.82rem; }
  .user-table th { padding: 7px 8px; font-size: 0.64rem; }

  /* Avatar smaller */
  .avatar { width: 36px; height: 36px; font-size: 0.68rem; }

  /* Action buttons compact */
  .btn-edit, .btn-id-card, .btn-delete { padding: 7px 8px; font-size: 0.95rem; }
  .action-cell { gap: 3px; }

  /* Modal: bottom sheet */
  .modal-overlay { padding: 0; align-items: flex-end; }
  .modal-box {
    border-radius: 18px 18px 0 0;
    max-width: 100%;
    max-height: 88vh;
    padding: 20px 16px 28px;
  }
  .form-grid { grid-template-columns: 1fr; gap: 12px; }
  .modal-actions { flex-direction: column-reverse; gap: 8px; }
  .btn-cancel, .btn-save { width: 100%; text-align: center; padding: 12px; }
}
</style>
