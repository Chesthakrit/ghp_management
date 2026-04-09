<template>
  <div class="attendance-dashboard">
    <div class="dashboard-header">
      <h2><i class="fas fa-calendar-check"></i> Attendance Dashboard</h2>
      <p class="subtitle">ภาพรวมการลงเวลาทำงานของพนักงาน</p>
    </div>

    <div class="dashboard-content">
      <div v-if="loading" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i>
        <span>กำลังโหลดข้อมูลพนักงาน...</span>
      </div>

      <!-- Dashboard Layout -->
      <div v-else class="dashboard-layout">
        
        <!-- Left Sidebar: Employee List -->
        <div class="employee-sidebar">
          <h3 class="section-title">พนักงานทั้งหมด ({{ users.length }})</h3>
          <div class="employee-list">
            <div v-for="user in users" :key="user.id" class="employee-card">
              <div class="emp-photo-wrapper">
                <img v-if="user.photo_path" :src="`${apiBase}/${user.photo_path}`" class="emp-photo" alt="Profile Photo" />
                <div v-else class="emp-photo-placeholder">
                  {{ user.first_name ? user.first_name[0].toUpperCase() : user.username[0].toUpperCase() }}
                </div>
              </div>
              <div class="emp-info">
                <p class="emp-name" :title="`${user.first_name} ${user.last_name}`">
                  {{ user.first_name }} {{ user.last_name }}
                </p>
                <p class="emp-role">
                  {{ user.employee_profile?.job_title || 'No Position' }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Main Area: Reports -->
        <div class="report-area">
          <div class="report-placeholder">
            <i class="fas fa-chart-line"></i>
            <p>เลือกพนักงานเพื่อดูรายงานเวลาเข้างาน...</p>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const apiBase = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

const loading = ref(false)
const users = ref([])

onMounted(async () => {
  await fetchUsers()
})

const fetchUsers = async () => {
  try {
    loading.value = true
    const response = await api.get('/users/')
    // กรองไม่เอาพนักงานที่สถานะเป็น terminated (ลาออก/ถูกเชิญออก) และไม่เอา Admin หลัก
    users.value = response.data.filter(u => {
      const status = u.employee_profile?.employment_status
      const isTerminated = status === 'terminated'
      
      const roleName = (u.role?.name || '').toLowerCase()
      const isSystemAdmin = u.username.toLowerCase() === 'admin' || roleName === 'admin'
      
      return !isTerminated && !isSystemAdmin
    })
  } catch (error) {
    console.error("Error fetching users:", error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.attendance-dashboard {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.dashboard-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.dashboard-header h2 {
  font-size: 1.8rem;
  color: #1e293b;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.dashboard-header h2 i {
  color: #3b82f6;
}

.subtitle {
  color: #64748b;
  margin: 0;
  font-size: 0.95rem;
}

.dashboard-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #64748b;
  font-size: 1.1rem;
  gap: 12px;
}

.loading-state i {
  font-size: 2rem;
  color: #3b82f6;
}

/* Layout Split */
.dashboard-layout {
  display: flex;
  gap: 24px;
  height: 100%;
  min-height: 0;
}

/* Left Sidebar */
.employee-sidebar {
  flex: 0 0 280px;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid #e2e8f0;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 1.05rem;
  color: #1e293b;
  font-weight: 800;
  padding-bottom: 12px;
  border-bottom: 2px dashed #cbd5e1;
}

.employee-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  padding-right: 6px;
}

/* Custom Scrollbar for List */
.employee-list::-webkit-scrollbar { width: 5px; }
.employee-list::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
.employee-list::-webkit-scrollbar-track { background: transparent; }

/* Employee Card (Horizontal Match) */
.employee-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  transition: all 0.2s ease;
  cursor: pointer;
}

.employee-card:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 10px rgba(0,0,0,0.06);
  border-color: #3b82f6;
}

.emp-photo-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid #f1f5f9;
  background: #e2e8f0;
  flex-shrink: 0;
}

.emp-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.emp-photo-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  font-weight: 800;
  color: #94a3b8;
  background: #f1f5f9;
}

.emp-info {
  flex: 1;
  min-width: 0; /* Prevents flex flex-wrap issues */
}

.emp-name {
  margin: 0 0 2px 0;
  font-weight: 750;
  color: #1e293b;
  font-size: 0.95rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.emp-role {
  margin: 0;
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Right Main Area */
.report-area {
  flex: 1;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.report-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #94a3b8;
  text-align: center;
}

.report-placeholder i {
  font-size: 3.5rem;
  color: #e2e8f0;
  margin-bottom: 20px;
}

.report-placeholder p {
  font-size: 1.1rem;
  font-weight: 500;
}

@media (max-width: 768px) {
  .dashboard-layout {
    flex-direction: column;
  }
  .employee-sidebar {
    flex: none;
    max-height: 300px; /* Limit height on mobile */
  }
  .report-area {
    min-height: 400px;
  }
}
</style>
