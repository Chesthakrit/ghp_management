<template>
  <div class="user-management">
    <!-- Stats Overview -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-number">{{ users.length }}</div>
        <div class="stat-label">Total</div>
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
                <span class="sort-label"><i class="fas fa-sort-amount-down"></i> Sort:</span>
                <button
                  :class="['sort-btn', { active: sortBy === 'dept' }]"
                  @click="toggleSort('dept')"
                >
                  <i class="fas fa-building"></i> Dept
                  <span v-if="sortBy === 'dept'" class="sort-arrow">{{ sortDir === 'asc' ? '↑' : '↓' }}</span>
                </button>
                <button
                  :class="['sort-btn', { active: sortBy === 'hire_date' }]"
                  @click="toggleSort('hire_date')"
                >
                  <i class="fas fa-calendar-check"></i> Hire Date
                  <span v-if="sortBy === 'hire_date'" class="sort-arrow">{{ sortDir === 'asc' ? '↑' : '↓' }}</span>
                </button>
                <button v-if="sortBy" class="sort-btn clear" @click="sortBy = ''; sortDir = 'asc'">
                  <i class="fas fa-times"></i> Clear
                </button>
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
                  <div 
                    class="name-info" 
                    :class="{ 'clickable-name': isAdmin || hasPerm('action.user.view_profile') }"
                    @click="(isAdmin || hasPerm('action.user.view_profile')) && $emit('view-profile', user.id)"
                  >
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
              <td class="hide-tablet">
                <span :class="['emp-status-badge', user.employee_profile?.employment_status || 'intern']">
                  {{ empStatusLabel(user.employee_profile?.employment_status) }}
                </span>
              </td>
              <td class="hide-tablet date-cell">{{ fmtDate(user.employee_profile?.hire_date) }}</td>
              <td class="action-cell">
                <template v-if="!isProtected(user)">
                  <button v-if="isAdmin || hasPerm('action.user.edit_identity')" class="btn-id-card" @click="openEditIdentity(user)" title="Identity">
                    <i class="fas fa-id-badge"></i>
                  </button>
                  <button v-if="isAdmin || hasPerm('action.user.edit_employment')" class="btn-edit" @click="openEdit(user)" title="Edit">
                    <i class="fas fa-user-edit"></i>
                  </button>
                  <button v-if="isAdmin || hasPerm('action.user.delete')" class="btn-delete" @click="deleteUser(user)" title="Delete">
                    <i class="fas fa-trash-alt"></i>
                  </button>
                  <span v-if="!isAdmin && !hasPerm('action.user.edit_identity') && !hasPerm('action.user.edit_employment') && !hasPerm('action.user.delete')" class="no-perms-text">
                    <i class="fas fa-lock"></i> No Access
                  </span>
                </template>
                 <span v-else class="admin-lock-badge">
                   <i class="fas fa-shield-alt"></i> {{ (user.employee_profile?.job_title || '').toLowerCase() === 'ceo' ? 'CEO Locked' : 'Admin Locked' }}
                </span>
              </td>
            </tr>
            <tr v-if="filteredUsers.length === 0">
              <td colspan="8" class="empty-row">No records found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ─── Edit User Modal ─── -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-box">
        <h3><i class="fas fa-user-cog"></i> Employment & Access</h3>
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
            <select v-model="form.department" class="form-input" @change="form.job_title = ''">
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
            <label>Employment Status</label>
            <select v-model="form.employment_status" class="form-input">
              <option value="intern">Intern</option>
              <option value="permanent">Permanent</option>
              <option value="terminated">Terminated</option>
            </select>
          </div>
          <div class="form-group">
            <label>Salary Type</label>
            <select v-model="form.salary_type" class="form-input">
              <option value="monthly">Monthly</option>
              <option value="daily">Daily</option>
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

    <!-- Photo Popup -->
    <div v-if="photoPopup" class="photo-popup-overlay" @click.self="closePhoto">
      <div class="photo-popup-box">
        <img :src="photoPopup" class="popup-img" />
        <button class="popup-close" @click="closePhoto">&times;</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import Swal from 'sweetalert2'

const emit = defineEmits(['go-to-identity', 'view-profile'])

const apiBase = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'
const users = ref([])
const currentUser = ref(null)
const departments = ref([])
const jobTitlesByDept = ref({})
const isLoading = ref(false)
const isSaving = ref(false)

const searchQuery  = ref('')
const filterDept   = ref('')
const sortBy       = ref('')
const sortDir      = ref('asc')
const showModal = ref(false)
const editingUser = ref(null)
const photoPopup = ref(null)

const form = ref({
  first_name: '',
  last_name: '',
  department: '',
  job_title: '',
  role: '',
  is_active: true,
  hire_date: '',
  employment_status: 'intern',
  salary_type: 'monthly'
})

const openPhoto  = (url) => { photoPopup.value = url }
const closePhoto = ()    => { photoPopup.value = null }

const isAdmin = computed(() => {
  const role = (localStorage.getItem('user_role') || '').toLowerCase()
  const uname = (localStorage.getItem('username') || '').toLowerCase()
  return role === 'admin' || uname === 'admin'
})

const hasPerm = (p) => {
  if (isAdmin.value) return true
  const perms = JSON.parse(localStorage.getItem('user_permissions') || '[]')
  return perms.includes(p)
}

const isProtected = (targetUser) => {
  if (!targetUser) return false
  const role = (targetUser.role || '').toLowerCase()
  const uname = (targetUser.username || '').toLowerCase()
  const jt = (targetUser.employee_profile?.job_title || '').toLowerCase()
  
  // Admin is always locked for safety or self-edit handled separately
  if (role === 'admin' || uname === 'admin') return true
  
  // CEO is locked if you are NOT an admin
  if (jt === 'ceo' && !isAdmin.value) return true
  
  return false
}

const deptLabel = (val) => departments.value.find(d => d.value === val)?.name || val || '—'

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
    
    // Security: Only 'admin' can see the 'admin' account in the list
    const isTargetAdmin = u.username.toLowerCase() === 'admin' || (u.role || '').toLowerCase() === 'admin'
    const isViewerAdmin = (localStorage.getItem('username') || '').toLowerCase() === 'admin'
    
    if (isTargetAdmin && !isViewerAdmin) return false
    
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
      return sortDir.value === 'asc' ? da.localeCompare(db) : db.localeCompare(da)
    })
  }

  return list
})

const toggleSort = (field) => {
  if (sortBy.value === field) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value  = field
    sortDir.value = 'asc'
  }
}

const fetchHRData = async () => {
  try {
    const [deptsRes, jobsRes] = await Promise.all([
      api.get('/hr/departments'),
      api.get('/hr/job-titles')
    ])
    
    departments.value = deptsRes.data.map(d => ({ ...d, label: d.name }))
    
    const grouped = {}
    jobsRes.data.forEach(job => {
      const deptObj = departments.value.find(d => d.id === job.department_id)
      if (deptObj) {
        if (!grouped[deptObj.value]) grouped[deptObj.value] = []
        grouped[deptObj.value].push(job.name)
      }
    })
    jobTitlesByDept.value = grouped
  } catch (e) {
    console.error('Error fetching HR data:', e)
  }
}

const fetchData = async () => {
  isLoading.value = true
  try {
    await fetchHRData()
    const usersRes = await api.get('/users/')
    users.value = usersRes.data
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
    salary_type: user.employee_profile?.salary_type || 'monthly',
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
  try {
    await api.put(`/users/${editingUser.value.id}`, {
      role: form.value.role,
      is_active: form.value.is_active,
      first_name: form.value.first_name,
      last_name: form.value.last_name,
    })

    await api.put(`/users/${editingUser.value.id}/profile`, {
      department: form.value.department,
      job_title: form.value.job_title,
      hire_date: form.value.hire_date,
      employment_status: form.value.employment_status,
      salary_type: form.value.salary_type,
    })

    Swal.fire({ icon: 'success', title: 'Saved successfully!', timer: 1500, showConfirmButton: false })
    closeModal()
    fetchData()
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
    cancelButtonColor: '#1a2a3a',
    reverseButtons: true,
  })
  if (!result.isConfirmed) return

  try {
    await api.delete(`/users/${user.id}`)
    users.value = users.value.filter(u => u.id !== user.id)
  } catch (e) {
    Swal.fire('Error', e.response?.data?.detail || 'Failed to delete user', 'error')
  }
}

onMounted(fetchData)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600&family=Outfit:wght@300;400;500;600;700&display=swap');

.user-management {
  width: 100%;
  font-family: 'Outfit', 'Kanit', sans-serif;
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ═══════════ STATS ROW ═══════════ */
.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.stat-card {
  background: white;
  border-radius: 12px;
  padding: 16px 24px;
  border: 1px solid #dde3e8;
  min-width: 100px;
  text-align: center;
  flex: 1;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
.stat-number { font-size: 1.8rem; font-weight: 700; color: #1a2a3a; }
.stat-label  { font-size: 0.76rem; color: #7a9bb0; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; }

/* ═══════════ SECTION CARD ═══════════ */
.section-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #dde3e8;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}
.section-header h2 { 
  margin: 0; 
  font-size: 0.95rem; 
  font-weight: 700; 
  color: #1a2a3a; 
  letter-spacing: 0.05em; 
  text-transform: uppercase;
  display: flex;
  align-items: center;
  gap: 8px;
}
.section-header h2::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 18px;
  background: #3b82f6;
  border-radius: 2px;
}

/* ═══════════ SEARCH & CONTROLS ═══════════ */
.controls-row {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-end;
}
.search-row { display: flex; gap: 10px; flex-wrap: wrap; }
.search-input, .filter-select {
  padding: 9px 14px;
  border: 1px solid #ccd6de;
  border-radius: 8px;
  font-family: 'Kanit', sans-serif;
  font-size: 0.9rem;
  background: #f7f9fa;
  color: #1a2a3a;
  transition: all 0.2s;
}
.search-input:focus, .filter-select:focus { 
  outline: none; 
  border-color: #3b82f6; 
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
.search-input { width: 240px; }

/* ═══════════ SORT CONTROLS ═══════════ */
.sort-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.sort-label {
  font-size: 0.74rem;
  color: #7a9bb0;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.sort-btn {
  padding: 6px 14px;
  border: 1px solid #ccd6de;
  border-radius: 20px;
  background: #f7f9fa;
  color: #4a6070;
  font-size: 0.8rem;
  font-family: inherit;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}
.sort-btn:hover { background: #e8ecef; border-color: #4a6070; color: #1a2a3a; }
.sort-btn.active {
  background: #1a2a3a;
  border-color: #1a2a3a;
  color: #fff;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.sort-btn.clear { border-color: #f1f5f9; color: #ef4444; background: transparent; }
.sort-btn.clear:hover { background: #fee2e2; color: #b91c1c; border-color: #fecaca; }

/* ═══════════ TABLE ═══════════ */
.table-wrapper { 
  overflow-x: auto; 
  border-radius: 8px;
  border: 1px solid #edf0f2;
}
.user-table { width: 100%; border-collapse: collapse; }
.user-table th {
  text-align: left;
  padding: 12px 16px;
  background: #f8fafc;
  font-size: 0.74rem;
  color: #4a6070;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  border-bottom: 1px solid #dde3e8;
  white-space: nowrap;
}
.user-table td { 
  padding: 14px 16px; 
  border-bottom: 1px solid #edf0f2; 
  vertical-align: middle; 
  font-size: 0.9rem; 
  color: #2c3e50; 
}
.user-table tr:hover td { background: #fdfdfd; }

.show-mobile { display: none; }

.name-cell { display: flex; align-items: center; gap: 12px; }
.avatar {
  width: 44px; height: 44px;
  border-radius: 50%;
  background: #1a2a3a;
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.85rem; font-weight: 700;
  flex-shrink: 0;
  overflow: hidden;
  transition: box-shadow 0.2s, transform 0.2s;
}
.avatar.has-photo:hover { 
  transform: scale(1.05);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2); 
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; }

.name-info { display: flex; flex-direction: column; gap: 2px; }
.name-text { font-weight: 600; color: #1a2a3a; font-size: 0.95rem; }
.nickname-text { font-size: 0.78rem; color: #64748b; font-weight: 500; }
.job-title-sub { font-size: 0.76rem; color: #3b82f6; font-style: normal; margin-top: 2px; font-weight: 500; }

.dept-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.72rem;
  font-weight: 700;
  background: #e0f2fe;
  color: #0369a1;
  border: 1px solid #bae6fd;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.emp-status-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.emp-status-badge.intern { background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }
.emp-status-badge.permanent { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
.emp-status-badge.terminated { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }

.date-cell { font-size: 0.85rem; color: #64748b; font-weight: 500; }

.action-cell { display: flex; gap: 8px; justify-content: flex-start; }
.btn-edit, .btn-id-card, .btn-delete {
  background: white;
  color: #1a2a3a;
  border: 1px solid #e2e8f0;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  width: 36px;
  height: 36px;
}
.btn-edit:hover { background: #f0f9ff; border-color: #3b82f6; color: #3b82f6; transform: translateY(-2px); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
.btn-id-card:hover { background: #fdf4ff; border-color: #d946ef; color: #d946ef; transform: translateY(-2px); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
.btn-delete:hover { background: #fef2f2; border-color: #ef4444; color: #ef4444; transform: translateY(-2px); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }

/* Modal Styles */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
}
.modal-box {
  background: white; padding: 32px; border-radius: 16px;
  width: 90%; max-width: 520px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}
.modal-box h3 { margin: 0 0 24px 0; font-size: 1.25rem; font-weight: 700; color: #1a2a3a; border-bottom: 2px solid #f1f5f9; padding-bottom: 12px; }

.modal-user-info { display: flex; align-items: center; gap: 16px; margin-bottom: 28px; background: #f8fafc; padding: 16px; border-radius: 12px; border: 1px solid #e2e8f0; }
.avatar.large { width: 64px; height: 64px; font-size: 1.4rem; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.form-group label { font-size: 0.78rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; display: block; }
.form-input { 
  padding: 10px 14px; border: 1px solid #ccd6de; border-radius: 8px; 
  font-family: inherit; font-size: 0.95rem; width: 100%; box-sizing: border-box;
  transition: border-color 0.2s;
}
.form-input:focus { outline: none; border-color: #3b82f6; }

.modal-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 32px; }
.btn-save { background: #3b82f6; color: #fff; border: none; padding: 10px 24px; border-radius: 8px; cursor: pointer; font-weight: 600; transition: background 0.2s; }
.btn-save:hover { background: #2563eb; }
.btn-cancel { background: #f8fafc; border: 1px solid #e2e8f0; color: #64748b; padding: 10px 24px; border-radius: 8px; cursor: pointer; font-weight: 600; }
.btn-cancel:hover { background: #f1f5f9; }

.loading { text-align: center; padding: 60px; color: #64748b; font-size: 1.1rem; }

/* Photo Popup */
.photo-popup-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.8);
  display: flex; align-items: center; justify-content: center; z-index: 2000;
}
.photo-popup-box { position: relative; max-width: 90%; max-height: 90%; }
.popup-img { max-width: 100%; max-height: 80vh; border-radius: 8px; }
.popup-close {
  position: absolute; top: -40px; right: 0; background: none; border: none;
  color: white; font-size: 2rem; cursor: pointer;
}

@media (max-width: 768px) {
  .hide-tablet, .hide-mobile { display: none !important; }
  .show-mobile { display: block !important; }
  .form-grid { grid-template-columns: 1fr; }
  .stats-row { flex-direction: column; }
  .section-card { padding: 16px; }
  .modal-box { padding: 20px; width: 95%; max-height: 90vh; overflow-y: auto; }
}
</style>
