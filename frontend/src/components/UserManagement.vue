<template>
  <div class="user-management-container">
    <h2>จัดการผู้ใช้งาน (User Management)</h2>
    
    <table class="user-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Username</th>
          <th>Email</th>
          <th>ตำแหน่งปัจจุบัน (Role)</th>
          <th>เปลี่ยนตำแหน่ง</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.username }}</td>
          <td>{{ user.email }}</td>
          <td>
            <!-- user.role จะเป็น String ชื่อ Role ตามที่เราแก้ใน Schema UserOut -->
            <span class="role-badge" :class="user.role">{{ user.role }}</span>
          </td>
          <td>
            <select 
              :value="user.role" 
              @change="updateRole(user, $event.target.value)"
              class="role-select"
            >
              <option v-for="role in roles" :key="role.id" :value="role.name">
                {{ role.name }}
              </option>
            </select>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'

const users = ref([])
const roles = ref([])

const fetchData = async () => {
  const token = localStorage.getItem('token')
  try {
    const [usersRes, rolesRes] = await Promise.all([
      // ต้องสร้าง API list users ก่อน (เดี๋ยวเราไปเพิ่มใน Backend)
      // สมมติว่ามี GET /users/ (Admin Only)
      axios.get('http://127.0.0.1:8000/users/', { headers: { Authorization: `Bearer ${token}` } }),
      axios.get('http://127.0.0.1:8000/roles/', { headers: { Authorization: `Bearer ${token}` } })
    ])
    users.value = usersRes.data
    roles.value = rolesRes.data
  } catch (error) {
    console.error(error)
    Swal.fire('Error', 'ไม่สามารถโหลดข้อมูลผู้ใช้ได้', 'error')
  }
}

const updateRole = async (user, newRoleName) => {
  const token = localStorage.getItem('token')
  try {
    // ต้องมี API เปลี่ยน Role 
    // สมมติ PUT /users/{id}/role body: { role: "new_role" }
    // แต่เรายังไม่ได้ทำ Endpoint นี้ใน Backend ชัดเจน (ทำแค่ create_role)
    // เดี๋ยวต้องไปเพิ่ม Endpoint นี้ใน users.py
    await axios.put(`http://127.0.0.1:8000/users/${user.id}/role`, 
      { role: newRoleName }, 
      { headers: { Authorization: `Bearer ${token}` } }
    )
    
    user.role = newRoleName // Update Local UI
    Swal.fire({
      icon: 'success',
      title: 'Updated',
      text: `เปลี่ยนตำแหน่ง ${user.username} เป็น ${newRoleName} แล้ว`,
      timer: 1500,
      showConfirmButton: false
    })
  } catch (error) {
    console.error(error)
    Swal.fire('Error', 'เปลี่ยนตำแหน่งไม่สำเร็จ', 'error')
    // Revert UI if needed (refresh)
    fetchData()
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.user-management-container {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-top: 20px;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
}

.user-table th, .user-table td {
  padding: 12px;
  border-bottom: 1px solid #eee;
}

.role-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.85rem;
  background: #eee;
}
.role-badge.admin { background: #ffeba7; color: #5a4b11; }
.role-badge.manager { background: #d1ecf1; color: #0c5460; }
.role-badge.employee { background: #d4edda; color: #155724; }

.role-select {
  padding: 6px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
</style>
