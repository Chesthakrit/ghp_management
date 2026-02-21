<template>
  <div class="identity-editor-container">

    <!-- ─── Mobile / Tablet Topbar ─── -->
    <div class="mobile-topbar">
      <button class="mobile-menu-btn" @click="sidebarOpen = true">☰</button>
      <span class="mobile-title">Employee Identity</span>
      <button class="mobile-back-btn" @click="$emit('go-back')">&#8592;</button>
    </div>

    <!-- ─── Overlay (mobile/tablet) ─── -->
    <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false"></div>

    <!-- Sidebar: Employee List -->
    <aside class="sidebar" :class="{ 'sidebar-open': sidebarOpen }">
      <div class="sidebar-header">
        <div class="sidebar-title">
          Employee Identity
          <button class="sidebar-close-btn" @click="sidebarOpen = false">✕</button>
        </div>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Search employees..." 
          class="search-input"
        />
      </div>
      <div class="employee-list">
        <div 
          v-for="user in filteredUsers" 
          :key="user.id" 
          :class="['employee-item', { active: selectedUser?.id === user.id }]"
          @click="selectUser(user); sidebarOpen = false"
        >
          <div class="emp-avatar">
            <img v-if="user.photo_path" :src="`${apiBase}/${user.photo_path}`" />
            <span v-else>{{ getInitials(user) }}</span>
          </div>
          <div class="emp-info">
            <div class="emp-name">{{ user.first_name || user.username }} {{ user.last_name || '' }}</div>
            <div class="emp-username">@{{ user.username }}</div>
          </div>
        </div>
        <div v-if="filteredUsers.length === 0" class="empty-msg">No employees found</div>
      </div>
      <button class="back-btn" @click="$emit('go-back')">Back to Panel</button>
    </aside>

    <!-- Main Content: Edit Form -->
    <main class="editor-main">
      <div v-if="selectedUser" class="editor-content">
        <div class="editor-header">
          <h2>Edit Employee Identity: {{ selectedUser.username }}</h2>
        </div>

        <div class="editor-body">
          <!-- Personal Information -->
          <div class="form-section">
            <h3 class="section-title">Personal Information</h3>
            <div class="input-grid">
              <div class="field-group">
                <label>First Name</label>
                <input type="text" v-model="formData.first_name" class="custom-input" />
              </div>
              <div class="field-group">
                <label>Last Name</label>
                <input type="text" v-model="formData.last_name" class="custom-input" />
              </div>
              <div class="field-group">
                <label>Nickname</label>
                <input type="text" v-model="formData.nickname" class="custom-input" />
              </div>
              <div class="field-group" style="grid-column: 1 / -1">
                <label>Date of Birth</label>
                <div class="dob-row">
                  <select v-model="dobDay" class="custom-input dob-select">
                    <option value="">Day</option>
                    <option v-for="d in 31" :key="d" :value="String(d).padStart(2,'0')">{{ d }}</option>
                  </select>
                  <select v-model="dobMonth" class="custom-input dob-select">
                    <option value="">Month</option>
                    <option v-for="(m, i) in monthNames" :key="i" :value="String(i+1).padStart(2,'0')">{{ m }}</option>
                  </select>
                  <select v-model="dobYear" class="custom-input dob-select">
                    <option value="">Year</option>
                    <option v-for="y in yearList" :key="y" :value="String(y)">{{ y }}</option>
                  </select>
                </div>
              </div>
              <div class="field-group">
                <label>Phone Number</label>
                <input type="tel" v-model="formData.phone" class="custom-input" />
              </div>
              <div class="field-group">
                <label>Nationality</label>
                <select v-model="formData.nationality" class="custom-input">
                  <option value="Thai">Thai</option>
                  <option value="Myanmar">Myanmar</option>
                  <option value="Cambodian">Cambodian</option>
                  <option value="Lao">Lao</option>
                  <option value="Vietnamese">Vietnamese</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Document Information -->
          <div class="form-section">
            <h3 class="section-title">Document Information</h3>
            <div class="input-grid">
              <div class="field-group" style="grid-column: 1 / -1">
                <label>ID Card / Passport Number</label>
                <input type="text" v-model="formData.id_card_number" class="custom-input" />
              </div>
            </div>
          </div>

          <!-- Media Updates -->
          <div class="form-section">
            <h3 class="section-title">Photos &amp; Documents</h3>
            <div class="upload-grid">
              <div class="upload-item">
                <label>Portrait Photo</label>
                <div class="upload-box upload-box--portrait" @click="$refs.photoInput.click()">
                  <img v-if="previewPhoto" :src="previewPhoto" />
                  <img v-else-if="selectedUser.photo_path" :src="`${apiBase}/${selectedUser.photo_path}?t=${cacheBust}`" />
                  <div v-else class="placeholder">
                    <span class="upload-icon">👤</span>
                    <span>Click to upload</span>
                    <span class="upload-hint">Portrait (3×4)</span>
                  </div>
                </div>
                <input ref="photoInput" type="file" accept="image/*" style="display:none" @change="handleFileChange($event, 'photo')" />
              </div>
              <div class="upload-item">
                <label>ID / Passport Document</label>
                <div class="upload-box upload-box--landscape" @click="$refs.idDocInput.click()">
                  <img v-if="previewIdDoc && previewIdDoc !== '__pdf__'" :src="previewIdDoc" />
                  <div v-else-if="previewIdDoc === '__pdf__'" class="placeholder">
                    <span class="upload-icon">📄</span>
                    <span>PDF selected</span>
                    <span class="upload-hint">Ready to upload</span>
                  </div>
                  <img v-else-if="selectedUser.id_doc_path && selectedUser.id_doc_path.match(/\.(jpg|jpeg|png|gif)$/i)" :src="`${apiBase}/${selectedUser.id_doc_path}?t=${cacheBust}`" />
                  <div v-else-if="selectedUser.id_doc_path" class="placeholder">
                    <span class="upload-icon">📄</span>
                    <span>PDF / File Uploaded</span>
                    <span class="upload-hint">Click to replace</span>
                  </div>
                  <div v-else class="placeholder">
                    <span class="upload-icon">🎟️</span>
                    <span>Click to upload</span>
                    <span class="upload-hint">Landscape (ID Card / Passport)</span>
                  </div>
                </div>
                <input ref="idDocInput" type="file" accept="image/*,application/pdf" style="display:none" @change="handleFileChange($event, 'idDoc')" />
              </div>
            </div>
          </div>

          <div class="action-footer">
            <button class="save-btn" @click="handleUpdate" :disabled="isSaving">
              {{ isSaving ? 'Updating...' : 'Update Identity' }}
            </button>
          </div>
        </div>
      </div>
      <div v-else class="no-selection">
        <h3>Select an employee from the list to edit identity</h3>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import api from '../api'
import Swal from 'sweetalert2'

const apiBase = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

const props = defineProps({
  initialUserId: Number
})

const emit = defineEmits(['go-back'])

const sidebarOpen = ref(false)
const users = ref([])
const selectedUser = ref(null)
const searchQuery = ref('')
const isSaving = ref(false)
const previewPhoto = ref(null)
const previewIdDoc = ref(null)
const cacheBust    = ref(Date.now())

const formData = reactive({
  first_name: '',
  last_name: '',
  nickname: '',
  birth_date: '',
  phone: '',
  id_card_number: '',
  nationality: ''
})

const files = reactive({
  photo: null,
  idDoc: null
})

// ─── Date of Birth helpers ───
const monthNames = [
  'January','February','March','April','May','June',
  'July','August','September','October','November','December'
]
const currentYear = new Date().getFullYear()
const yearList = Array.from({ length: 80 }, (_, i) => currentYear - i)

// Split birth_date (YYYY-MM-DD) into three refs
const dobDay   = ref('')
const dobMonth = ref('')
const dobYear  = ref('')

// When any dropdown changes → update formData.birth_date
watch([dobDay, dobMonth, dobYear], ([d, m, y]) => {
  if (d && m && y) {
    formData.birth_date = `${y}-${m}-${d}`
  } else {
    formData.birth_date = ''
  }
})

const filteredUsers = computed(() => {
  const q = searchQuery.value.toLowerCase()
  return users.value.filter(u => {
    // กรองเอา admin และแผนก management ออก
    const isAdmin = u.role === 'admin'
    const isManagement = u.employee_profile?.department === 'management'
    if (isAdmin || isManagement) return false

    return u.username.toLowerCase().includes(q) || 
      (u.first_name || '').toLowerCase().includes(q) ||
      (u.last_name || '').toLowerCase().includes(q)
  })
})

const fetchUsers = async (reselectId = null) => {
  try {
    const res = await api.get('/users/')
    users.value = res.data

    // reselect ตาม id ที่ส่งมา หรือ initialUserId
    const targetId = reselectId || props.initialUserId
    if (targetId) {
      const u = users.value.find(user => user.id === targetId)
      if (u) selectUser(u)
    }
  } catch (e) {
    console.error(e)
  }
}

const selectUser = (user) => {
  selectedUser.value = user
  previewPhoto.value = null
  previewIdDoc.value = null
  files.photo = null
  files.idDoc = null
  
  // Fill form
  formData.first_name = user.first_name || ''
  formData.last_name = user.last_name || ''
  formData.nickname = user.nickname || ''
  formData.birth_date = user.birth_date || ''
  formData.phone = user.phone || ''
  formData.id_card_number = user.id_card_number || ''
  formData.nationality = user.nationality || ''

  // Populate DOB dropdowns
  if (user.birth_date) {
    const parts = user.birth_date.split('-')   // ['YYYY','MM','DD']
    dobYear.value  = parts[0] || ''
    dobMonth.value = parts[1] || ''
    dobDay.value   = parts[2] || ''
  } else {
    dobYear.value = dobMonth.value = dobDay.value = ''
  }
}

const handleFileChange = (e, type) => {
  const file = e.target.files[0]
  if (!file) return
  files[type] = file
  if (file.type.startsWith('image/')) {
    const url = URL.createObjectURL(file)
    if (type === 'photo') previewPhoto.value = url
    else previewIdDoc.value = url
  } else {
    // PDF หรือไฟล์อื่น — ล้าง preview แสดงข้อความแทน
    if (type !== 'photo') previewIdDoc.value = '__pdf__'
  }
  // Reset input ให้เลือกไฟล์เดิมซ้ำได้
  e.target.value = ''
}

const getInitials = (user) => {
  const f = user.first_name?.[0] || user.username?.[0] || '?'
  const l = user.last_name?.[0] || ''
  return (f + l).toUpperCase()
}

const handleUpdate = async () => {
  if (!selectedUser.value) return
  isSaving.value = true
  const currentUserId = selectedUser.value.id

  try {
    // 1. Update Profile Data
    await api.put(
      `/users/${currentUserId}`,
      {
        first_name: formData.first_name,
        last_name: formData.last_name,
        nickname: formData.nickname,
        birth_date: formData.birth_date,
        phone: formData.phone,
        id_card_number: formData.id_card_number,
        nationality: formData.nationality
      }
    )

    // 2. Upload files if any
    if (files.photo || files.idDoc) {
      const fd = new FormData()
      if (files.photo)  fd.append('photo',  files.photo)
      if (files.idDoc)  fd.append('id_doc', files.idDoc)
      await api.post(
        `/users/${currentUserId}/upload`,
        fd,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
    }

    await Swal.fire({
      icon: 'success',
      title: 'Identity Updated',
      timer: 1500,
      showConfirmButton: false
    })

    // Refresh + reselect user ที่กำลังแก้
    cacheBust.value = Date.now()
    await fetchUsers(currentUserId)
  } catch (e) {
    console.error(e)
    Swal.fire('Error', e.response?.data?.detail || 'Update failed', 'error')
  } finally {
    isSaving.value = false
  }
}

onMounted(fetchUsers)
</script>

<style scoped>
.identity-editor-container {
  display: flex;
  height: 100vh;
  background: #f2f4f6;
  font-family: 'Inter', sans-serif;
  position: relative;
}

/* ─── Mobile Topbar ─── */
.mobile-topbar {
  display: none;
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 100;
  background: #1a2a3a;
  color: #fff;
  padding: 12px 16px;
  align-items: center;
  justify-content: space-between;
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
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* ─── Sidebar Overlay ─── */
.sidebar-overlay {
  display: block;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  z-index: 199;
}

/* ─── Sidebar ─── */
.sidebar {
  width: 300px;
  background: #1a2a3a;
  color: #a8bcc8;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: transform 0.25s ease;
  z-index: 200;
}

.sidebar-header {
  padding: 24px;
  border-bottom: 1px solid #2e4057;
}

.sidebar-title {
  font-size: 1rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 15px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-close-btn {
  display: none;
  background: transparent;
  border: none;
  color: #7a9bb0;
  font-size: 1rem;
  cursor: pointer;
  line-height: 1;
  padding: 2px 6px;
}
.sidebar-close-btn:hover { color: #fff; }

.search-input {
  width: 100%;
  padding: 10px 12px;
  background: #243447;
  border: 1px solid #2e4057;
  color: #fff;
  border-radius: 6px;
  font-size: 0.9rem;
  box-sizing: border-box;
}

.employee-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.employee-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 4px;
}
.employee-item:hover  { background: #243447; }
.employee-item.active { background: #2e4057; color: #fff; }

.emp-avatar {
  width: 40px; height: 40px;
  border-radius: 50%;
  background: #2e4057;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
  font-size: 0.8rem; font-weight: 700;
  flex-shrink: 0;
}
.emp-avatar img { width: 100%; height: 100%; object-fit: cover; }
.emp-info { display: flex; flex-direction: column; }
.emp-name { font-size: 0.88rem; font-weight: 500; }
.emp-username { font-size: 0.75rem; color: #7a9bb0; }

.back-btn {
  margin: 20px;
  padding: 10px;
  background: transparent;
  border: 1px solid #2e4057;
  color: #7a9bb0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.back-btn:hover { background: #243447; color: #fff; }

/* ─── Main Editor ─── */
.editor-main {
  flex: 1;
  padding: 40px;
  overflow-y: auto;
  min-width: 0;
}

.editor-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  max-width: 900px;
  margin: 0 auto;
  padding: 40px;
}

.editor-header h2 {
  margin: 0 0 30px;
  font-size: 1.3rem;
  color: #1a2a3a;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
}

.form-section { margin-bottom: 30px; }
.section-title {
  font-size: 0.82rem; font-weight: 700;
  color: #1a2a3a; text-transform: uppercase;
  letter-spacing: 0.07em; margin-bottom: 15px;
}

.input-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

/* DOB row: three dropdowns side by side */
.dob-row {
  display: flex;
  gap: 8px;
}
.dob-select {
  flex: 1;
  min-width: 0;
}

.field-group { display: flex; flex-direction: column; gap: 6px; }
.field-group label {
  font-size: 0.75rem; font-weight: 700;
  color: #4a6070; text-transform: uppercase;
}

.custom-input {
  padding: 10px;
  border: 1px solid #ccd6de;
  border-radius: 6px;
  background: #f7f9fa;
  font-family: inherit;
  font-size: 0.9rem;
  color: #1a2a3a;
  width: 100%; box-sizing: border-box;
}
.custom-input:focus { outline: none; border-color: #1a2a3a; background: white; }

/* Upload area — side by side in one row */
.upload-grid {
  display: flex;
  flex-direction: row;
  gap: 20px;
  align-items: flex-start;
  justify-content: center;
}
.upload-item { display: flex; flex-direction: column; gap: 6px; align-items: center; }
.upload-item label { font-size: 0.73rem; font-weight: 700; color: #4a6070; text-transform: uppercase; white-space: nowrap; }

/* Base upload box */
.upload-box {
  border: 2px dashed #ccd6de;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f7f9fa;
  overflow: hidden;
  transition: border-color 0.2s, background 0.2s;
}
.upload-box:hover {
  border-color: #4a6070;
  background: #eef1f4;
}
.upload-box img { width: 100%; height: 100%; object-fit: cover; }

/* Portrait — 3:4, desktop size */
.upload-box--portrait {
  width: 200px;
  aspect-ratio: 3 / 4;
  flex-shrink: 0;
}
.upload-box--portrait img { object-fit: cover; }

/* Landscape — 8:5, desktop size */
.upload-box--landscape {
  width: 375px;
  flex-shrink: 0;
  aspect-ratio: 8 / 5;
}
.upload-box--landscape img { object-fit: contain; }

/* Placeholder content */
.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #7a9bb0;
  font-size: 0.78rem;
  padding: 10px 8px;
  text-align: center;
}
.upload-icon { font-size: 1.6rem; line-height: 1; }
.upload-hint { font-size: 0.66rem; color: #a8bcc8; }

.action-footer {
  margin-top: 40px; padding-top: 20px;
  border-top: 1px solid #eee;
  display: flex; justify-content: flex-end;
}

.save-btn {
  background: #1a2a3a; color: #a8bcc8;
  border: none; padding: 12px 40px;
  border-radius: 6px; font-weight: 700;
  cursor: pointer; transition: all 0.2s;
  font-family: inherit;
}
.save-btn:hover:not(:disabled) { background: #243447; color: #fff; }
.save-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.no-selection {
  display: flex; height: 100%;
  align-items: center; justify-content: center;
  color: #7a9bb0;
}
.empty-msg {
  text-align: center; padding: 20px;
  font-size: 0.85rem; color: #7a9bb0;
}

/* ═══════════════════════════════════════════
   RESPONSIVE — Tablet + Mobile  (≤ 1024px)
═══════════════════════════════════════════ */
@media (max-width: 1024px) {
  /* Show topbar */
  .mobile-topbar { display: flex; }

  /* Sidebar: fixed drawer */
  .sidebar {
    position: fixed;
    top: 0; left: 0; bottom: 0;
    width: 300px;
    transform: translateX(-100%);
    box-shadow: 4px 0 28px rgba(0,0,0,0.3);
    z-index: 300;
  }
  .sidebar.sidebar-open { transform: translateX(0); }
  .sidebar-close-btn { display: block; }

  /* Push content down below topbar */
  .editor-main { padding-top: 70px; }

  /* Editor card compact */
  .editor-content { padding: 24px; }
  .editor-header h2 { font-size: 1.1rem; }
}

/* ═══════════════════════════════════════════
   RESPONSIVE — Mobile only  (≤ 640px)
═══════════════════════════════════════════ */
@media (max-width: 640px) {
  .sidebar { width: 280px; }
  .editor-main { padding: 70px 14px 24px; }
  .editor-content { padding: 16px; border-radius: 8px; }
  .editor-header h2 { font-size: 0.95rem; margin-bottom: 16px; }
  .input-grid { grid-template-columns: 1fr; gap: 14px; }
  .upload-grid { gap: 12px; }
  .upload-box--portrait  { width: 110px; }
  .upload-box--landscape { width: 200px; }
  .upload-box--portrait { max-width: 180px; }
  .action-footer { justify-content: stretch; }
  .save-btn { width: 100%; padding: 12px; }
}
</style>
