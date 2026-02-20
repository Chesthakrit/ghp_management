<template>
  <div class="admin-panel">

    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-logo">
        <span>Admin Panel</span>
      </div>
      <nav class="sidebar-nav">
        <button 
          :class="['nav-item', { active: activeTab === 'users' }]"
          @click="activeTab = 'users'"
        >User Management</button>
        <button 
          :class="['nav-item', { active: activeTab === 'roles' }]"
          @click="activeTab = 'roles'"
        >Roles &amp; Permissions</button>
      </nav>
      <button class="back-btn" @click="$emit('go-back')">
        &larr; Back to Dashboard
      </button>
    </aside>

    <!-- Main Content -->
    <main class="admin-content">

      <!-- TAB: Users -->
      <div v-if="activeTab === 'users'">
        <!-- Stats Overview -->
        <div class="stats-row">
          <div class="stat-card">
            <div class="stat-number">{{ users.length }}</div>
            <div class="stat-label">พนักงานทั้งหมด</div>
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
            <div class="search-row">
              <input v-model="searchQuery" placeholder="Search name / username..." class="search-input" />
              <select v-model="filterDept" class="filter-select">
                <option value="">All Departments</option>
                <option v-for="d in departments" :key="d.value" :value="d.value">{{ d.label }}</option>
              </select>
            </div>
          </div>

            <div v-if="isLoading" class="loading">Loading...</div>

            <table v-else class="user-table">
              <thead>
                <tr>
                  <th>Full Name</th>
                  <th>Username</th>
                  <th>Department</th>
                  <th>Job Title</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Hire Date</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in filteredUsers" :key="user.id">
                  <td class="name-cell">
                    <div class="avatar" :class="{ 'has-photo': user.photo_path }" @click="user.photo_path && openPhoto('http://127.0.0.1:8000/' + user.photo_path)">
                      <img v-if="user.photo_path"
                        :src="'http://127.0.0.1:8000/' + user.photo_path"
                        class="avatar-img"
                        :alt="getInitials(user)"
                      />
                      <span v-else>{{ getInitials(user) }}</span>
                    </div>
                    <div class="name-info">
                      <span class="name-text">{{ user.first_name || '-' }} {{ user.last_name || '' }}</span>
                      <span v-if="user.nickname" class="nickname-text">({{ user.nickname }})</span>
                    </div>
                  </td>
                  <td class="username-cell">{{ user.username }}</td>
                  <td>
                    <span v-if="user.employee_profile?.department" class="dept-badge">
                      {{ deptLabel(user.employee_profile.department) }}
                    </span>
                    <span v-else class="no-data">—</span>
                  </td>
                  <td>{{ user.employee_profile?.job_title || '—' }}</td>
                  <td>
                    <span class="role-badge">{{ user.role }}</span>
                  </td>
                  <td>
                    <span :class="['emp-status-badge', user.employee_profile?.employment_status || 'intern']">
                      {{ empStatusLabel(user.employee_profile?.employment_status) }}
                    </span>
                  </td>
                  <td class="date-cell">{{ user.employee_profile?.hire_date || '—' }}</td>
                  <td class="action-cell">
                    <template v-if="user.role !== 'admin'">
                      <button class="btn-edit" @click="openEdit(user)">Edit</button>
                      <button class="btn-delete" @click="deleteUser(user)">Delete</button>
                    </template>
                    <span v-else class="admin-lock-badge">Master Admin</span>
                  </td>
                </tr>
                <tr v-if="filteredUsers.length === 0">
                  <td colspan="8" class="empty-row">No records found</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      <!-- TAB: Roles -->
      <div v-if="activeTab === 'roles'">
        <RoleManagement />
      </div>

    </main>

    <!-- Edit User Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-box">
        <h3>Edit Employee</h3>
        <div class="modal-user-info">
          <div class="avatar large">
            <img v-if="editingUser?.photo_path"
              :src="'http://127.0.0.1:8000/' + editingUser.photo_path"
              class="avatar-img"
            />
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
            <label>First Name</label>
            <input v-model="form.first_name" type="text" class="form-input" />
          </div>
          <div class="form-group">
            <label>Last Name</label>
            <input v-model="form.last_name" type="text" class="form-input" />
          </div>
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
              <option 
                v-for="role in availableRoles" 
                :key="role.id" 
                :value="role.name"
              >{{ role.name }}</option>
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
          <div class="form-group">
            <label>Hire Date</label>
            <input v-model="form.hire_date" type="date" class="form-input" />
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
import axios from 'axios'
import Swal from 'sweetalert2'
import RoleManagement from './RoleManagement.vue'

const emit = defineEmits(['go-back'])

const activeTab = ref('users')
const users = ref([])
const roles = ref([])
const isLoading = ref(false)
const isSaving = ref(false)
const searchQuery = ref('')
const filterDept = ref('')
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
  return users.value.filter(u => {
    const q = searchQuery.value.toLowerCase()
    const matchSearch = !q || 
      u.username.toLowerCase().includes(q) ||
      (u.first_name || '').toLowerCase().includes(q) ||
      (u.last_name || '').toLowerCase().includes(q)
    const matchDept = !filterDept.value || u.employee_profile?.department === filterDept.value
    return matchSearch && matchDept
  })
})

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
      axios.get('http://127.0.0.1:8000/users/', { headers: { Authorization: `Bearer ${token}` } }),
      axios.get('http://127.0.0.1:8000/roles/', { headers: { Authorization: `Bearer ${token}` } }),
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

const closeModal = () => {
  showModal.value = false
  editingUser.value = null
}

const saveUser = async () => {
  isSaving.value = true
  const token = localStorage.getItem('token')
  try {
    // 1. อัปเดตข้อมูลส่วนตัว + Role
    const userRes = await axios.put(
      `http://127.0.0.1:8000/users/${editingUser.value.id}`,
      {
        role: form.value.role,
        is_active: form.value.is_active,
        first_name: form.value.first_name,
        last_name: form.value.last_name,
      },
      { headers: { Authorization: `Bearer ${token}` } }
    )

    // 2. อัปเดตข้อมูลบริษัท (EmployeeProfile)
    const profileRes = await axios.put(
      `http://127.0.0.1:8000/users/${editingUser.value.id}/profile`,
      {
        department: form.value.department,
        job_title: form.value.job_title,
        hire_date: form.value.hire_date,
        employment_status: form.value.employment_status,
      },
      { headers: { Authorization: `Bearer ${token}` } }
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
    await axios.delete(`http://127.0.0.1:8000/users/${user.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    users.value = users.value.filter(u => u.id !== user.id)
    Swal.fire({ icon: 'success', title: 'Deleted', timer: 1000, showConfirmButton: false })
  } catch (e) {
    Swal.fire('Error', e.response?.data?.detail || 'Delete failed', 'error')
  }
}

onMounted(fetchData)
</script>

<style scoped>
/* ─── Color Palette (based on #1a2a3a) ────────────────────
  Dark  : #1a2a3a   (base dark navy)
  Mid   : #243447   (hover/active)
  Shade : #2e4057   (borders/dividers inside dark areas)
  Muted : #4a6070   (muted text on dark bg)
  Light : #e8ecef   (light bg tint from navy)
  Pale  : #f2f4f6   (page background)
  White : #ffffff
──────────────────────────────────────────────────────── */

.admin-panel {
  display: flex;
  min-height: 100vh;
  background: #f2f4f6;
  font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
}

/* Sidebar */
.sidebar {
  width: 220px;
  background: #1a2a3a;
  color: #a8bcc8;
  display: flex;
  flex-direction: column;
  padding: 20px 0;
  flex-shrink: 0;
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

/* Main */
.admin-content {
  flex: 1;
  padding: 28px;
  overflow-y: auto;
}

/* Stats */
.stats-row {
  display: flex;
  gap: 14px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.stat-card {
  background: white;
  border-radius: 8px;
  padding: 16px 24px;
  border: 1px solid #dde3e8;
  min-width: 110px;
  text-align: center;
}
.stat-number { font-size: 1.8rem; font-weight: 700; color: #1a2a3a; }
.stat-label { font-size: 0.78rem; color: #7a9bb0; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }

/* Section Card */
.section-card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  border: 1px solid #dde3e8;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}
.section-header h2 { margin: 0; font-size: 1rem; font-weight: 700; color: #1a2a3a; letter-spacing: 0.04em; text-transform: uppercase; }
.search-row { display: flex; gap: 8px; }
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
.search-input { width: 220px; }

/* Table */
.user-table { width: 100%; border-collapse: collapse; }
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
}
.user-table td { padding: 12px; border-bottom: 1px solid #edf0f2; vertical-align: middle; font-size: 0.88rem; color: #2c3e50; }
.user-table tr:hover td { background: #f7f9fa; }

.name-cell { display: flex; align-items: center; gap: 10px; }
.avatar {
  width: 44px; height: 44px;
  border-radius: 50%;
  background: #1a2a3a;
  color: #a8bcc8;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.78rem; font-weight: 700;
  flex-shrink: 0;
  letter-spacing: 0.03em;
  overflow: hidden;
  transition: box-shadow 0.15s;
}
.avatar.has-photo { cursor: pointer; }
.avatar.has-photo:hover { box-shadow: 0 0 0 2px #2e4057, 0 0 0 4px #a8bcc8; }
.avatar.large { width: 52px; height: 52px; font-size: 0.9rem; }
.avatar-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }

.name-info { display: flex; flex-direction: column; gap: 1px; }
.name-text { font-size: 0.88rem; color: #1a2a3a; font-weight: 500; }
.nickname-text { font-size: 0.76rem; color: #7a9bb0; }

.username-cell { color: #7a9bb0; font-size: 0.85rem; }
.no-data { color: #b0c4d0; }


/* Badges — #1a2a3a monotone scale */
.dept-badge {
  padding: 3px 9px;
  border-radius: 4px;
  font-size: 0.76rem;
  font-weight: 600;
  background: #e8ecef;
  color: #2e4057;
  border: 1px solid #ccd6de;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.emp-status-badge { padding: 3px 9px; border-radius: 4px; font-size: 0.76rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
.emp-status-badge.intern    { background: #e8ecef; color: #4a6070; border: 1px solid #ccd6de; }
.emp-status-badge.permanent { background: #2e4057; color: #c8d8e4; border: 1px solid #2e4057; }
.emp-status-badge.terminated{ background: #1a2a3a; color: #7a9bb0; border: 1px solid #1a2a3a; }

.date-cell { font-size: 0.85rem; color: #7a9bb0; }

.role-badge {
  padding: 3px 9px;
  border-radius: 4px;
  font-size: 0.76rem;
  font-weight: 700;
  background: #e8ecef;
  color: #1a2a3a;
  border: 1px solid #ccd6de;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.btn-edit {
  background: #1a2a3a; color: #a8bcc8;
  border: none; padding: 6px 14px;
  border-radius: 5px; cursor: pointer;
  font-family: inherit;
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  transition: background 0.15s;
}
.btn-edit:hover { background: #243447; color: #fff; }

.action-cell { display: flex; gap: 6px; align-items: center; }

.btn-delete {
  background: transparent; color: #8b3a3a;
  border: 1px solid #c0a0a0; padding: 6px 12px;
  border-radius: 5px; cursor: pointer;
  font-family: inherit;
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  transition: all 0.15s;
}
.btn-delete:hover { background: #8b3a3a; color: #fff; border-color: #8b3a3a; }


.admin-lock-badge {
  background: #f2f4f6;
  color: #7a9bb0;
  border: 1px solid #ccd6de;
  padding: 4px 10px;
  border-radius: 5px;
  font-size: 0.76rem;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.lock-hint {
  color: #7a9bb0;
  font-size: 0.76rem;
  margin-top: 4px;
}

.empty-row { text-align: center; color: #b0c4d0; padding: 40px !important; font-size: 0.88rem; }
.loading { text-align: center; padding: 40px; color: #7a9bb0; font-size: 0.88rem; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(26,42,58,0.45);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.modal-box {
  background: white;
  border-radius: 10px;
  padding: 28px;
  width: 560px; max-width: 95vw;
  max-height: 90vh; overflow-y: auto;
  border: 1px solid #dde3e8;
}
.modal-box h3 { margin: 0 0 16px; font-size: 0.95rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; color: #1a2a3a; }
.modal-user-info {
  display: flex; align-items: center; gap: 12px;
  padding: 12px; background: #f2f4f6;
  border-radius: 7px; margin-bottom: 20px;
  border: 1px solid #dde3e8;
}
.modal-user-info strong { display: block; color: #1a2a3a; font-size: 0.95rem; }
.modal-user-info span { font-size: 0.82rem; color: #7a9bb0; }
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}
.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-group label { font-size: 0.75rem; color: #4a6070; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }
.form-input {
  padding: 9px 10px;
  border: 1px solid #ccd6de; border-radius: 6px;
  font-family: inherit; font-size: 0.88rem;
  background: #f7f9fa; color: #1a2a3a;
}
.form-input:focus { outline: none; border-color: #2e4057; background: white; }
.form-input:disabled { background: #edf0f2; color: #7a9bb0; cursor: not-allowed; }
.modal-actions {
  display: flex; justify-content: flex-end; gap: 8px;
  margin-top: 22px;
  padding-top: 16px;
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
  letter-spacing: 0.03em;
  transition: background 0.15s;
}
.btn-save:hover:not(:disabled) { background: #243447; color: #fff; }
.btn-save:disabled { opacity: 0.4; cursor: not-allowed; }

/* Photo Popup */
.photo-popup-overlay {
  position: fixed; inset: 0;
  background: rgba(26,42,58,0.6);
  backdrop-filter: blur(3px);
  display: flex; align-items: center; justify-content: center;
  z-index: 2000;
}
.photo-popup-box {
  position: relative;
  background: white;
  border-radius: 10px;
  padding: 8px;
  box-shadow: 0 20px 60px rgba(26,42,58,0.4);
  max-width: 340px;
  width: 90vw;
}
.popup-img { width: 100%; border-radius: 6px; display: block; }
.popup-close {
  position: absolute;
  top: -10px; right: -10px;
  width: 28px; height: 28px;
  border-radius: 50%;
  background: #1a2a3a; color: #a8bcc8;
  border: none; font-size: 1.1rem; line-height: 1;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: background 0.15s;
}
.popup-close:hover { background: #243447; color: #fff; }
</style>
