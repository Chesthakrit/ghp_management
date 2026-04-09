<template>
  <div class="attendance-dashboard">
    <div class="dashboard-header">
      <h2><i class="fas fa-calendar-check"></i> Attendance Dashboard</h2>
      <p class="subtitle">ภาพรวมการลงเวลาทำงานของพนักงาน</p>
    </div>

    <div class="dashboard-content">
      <!-- พื้นที่สำหรับใส่เนื้อหา เช่น กราฟตารางสถิติ หรือสรุปเวลาการทำงาน -->
      <div class="placeholder-card">
        <i class="fas fa-chart-line"></i>
        <p>กำลังพัฒนาข้อมูลสถิติการลงเวลา...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

// ตัวอย่าง State สำหรับเก็บข้อมูล
const loading = ref(false)
const attendanceData = ref([])

onMounted(async () => {
  // ดึงข้อมูล Attendance จากหลังบ้าน
  // fetchData()
})

const fetchData = async () => {
  try {
    loading.value = true
    // const response = await api.get('/attendance/summary')
    // attendanceData.value = response.data
  } catch (error) {
    console.error("Error fetching attendance data:", error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.attendance-dashboard {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
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
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.placeholder-card {
  background: #f8fafc;
  border: 1px dashed #cbd5e0;
  border-radius: 12px;
  padding: 60px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
}

.placeholder-card i {
  font-size: 3rem;
  margin-bottom: 16px;
  color: #e2e8f0;
}

@media (max-width: 768px) {
  .attendance-dashboard {
    padding: 16px;
  }
}
</style>
