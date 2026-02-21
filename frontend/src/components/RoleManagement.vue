<template>
  <div class="role-management-container">
    <div class="header">
      <h2>จัดการตำแหน่ง (Manage Roles)</h2>
      <button class="btn-create" @click="openCreateModal">+ สร้างตำแหน่งใหม่</button>
    </div>

    <!-- ตารางแสดง Role -->
    <table class="role-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>ชื่อตำแหน่ง (Role Name)</th>
          <th>สิทธิ์การเข้าถึง (Permissions)</th>
          <th>จัดการ</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="role in roles" :key="role.id">
          <td>{{ role.id }}</td>
          <td>
            <span class="role-badge">{{ role.name }}</span>
          </td>
          <td>
            <div class="permissions-list">
              <span v-for="perm in role.permissions" :key="perm" class="perm-tag">
                {{ perm }}
              </span>
              <span v-if="role.permissions.length === 0" class="no-perm">- ไม่มีสิทธิ์ -</span>
            </div>
          </td>
          <td>
            <button class="btn-edit" @click="openEditModal(role)">แก้ไข</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Modal สร้าง/แก้ไข Role -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <h3>{{ isEditing ? 'แก้ไขตำแหน่ง' : 'สร้างตำแหน่งใหม่' }}</h3>
        
        <div class="form-group">
          <label>ชื่อตำแหน่ง (Role Name):</label>
          <input v-model="form.name" type="text" placeholder="เช่น Manager, HR" :disabled="isEditing && form.name === 'admin'">
          <small v-if="isEditing && form.name === 'admin'" class="text-danger">ไม่สามารถเปลี่ยนชื่อ Admin ได้</small>
        </div>

        <div class="form-group">
          <label>เลือกสิทธิ์ (Permissions):</label>
          <div class="permissions-grid">
            <div v-for="perm in availablePermissions" :key="perm.id" class="perm-item">
              <input 
                type="checkbox" 
                :id="perm.id" 
                :value="perm.id" 
                v-model="form.permissions"
              >
              <label :for="perm.id">{{ perm.name }}</label>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-cancel" @click="closeModal">ยกเลิก</button>
          <button class="btn-save" @click="saveRole">บันทึก</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import Swal from 'sweetalert2'

const roles = ref([])
const availablePermissions = ref([])
const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)

const form = ref({
  name: '',
  permissions: []
})

// ดึงข้อมูล Roles และ Permissions จาก API
const fetchData = async () => {
  const token = localStorage.getItem('token')
  try {
    const [rolesRes, permsRes] = await Promise.all([
      api.get('/roles/'),
      api.get('/permissions/')
    ])
    roles.value = rolesRes.data
    availablePermissions.value = permsRes.data
  } catch (error) {
    console.error(error)
    Swal.fire('Error', 'ไม่สามารถโหลดข้อมูลได้ (คุณอาจไม่มีสิทธิ์)', 'error')
  }
}

const openCreateModal = () => {
  isEditing.value = false
  editingId.value = null
  form.value = { name: '', permissions: [] }
  showModal.value = true
}

const openEditModal = (role) => {
  isEditing.value = true
  editingId.value = role.id
  // Copy data to form
  form.value = {
    name: role.name,
    permissions: [...role.permissions] // clone array
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const saveRole = async () => {
  const token = localStorage.getItem('token')
  if (!form.value.name) return Swal.fire('Error', 'กรุณากรอกชื่อตำแหน่ง', 'warning')

  try {
    if (isEditing.value) {
      // Update
      await api.put(`/roles/${editingId.value}`, form.value)
    } else {
      await api.post('/roles/', form.value)
    }
    
    Swal.fire('Success', 'บันทึกเรียบร้อย', 'success')
    closeModal()
    fetchData() // Reload
  } catch (error) {
    console.error(error)
    Swal.fire('Error', 'บันทึกไม่สำเร็จ', 'error')
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.role-management-container {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.role-table {
  width: 100%;
  border-collapse: collapse;
}

.role-table th, .role-table td {
  padding: 12px;
  border-bottom: 1px solid #eee;
  text-align: left;
}

.role-badge {
  background: #e3f2fd;
  color: #1565c0;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: bold;
}

.perm-tag {
  background: #f5f5f5;
  border: 1px solid #ddd;
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 0.85rem;
  margin-right: 4px;
  margin-bottom: 4px;
  display: inline-block;
}

.btn-create {
  background: #2ecc71;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-edit {
  background: #f1c40f;
  color: #333;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
}

.form-group input[type="text"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.permissions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #eee;
  padding: 10px;
}

.perm-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn-cancel {
  background: #ccc;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-save {
  background: #3498db;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}
</style>
