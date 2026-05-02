<template>
  <div class="attendance-dashboard">
    <div class="dashboard-header">
      <div class="header-main">
        <h2><i class="fas fa-calendar-check"></i> Attendance Dashboard</h2>
        <p class="subtitle">Daily Overview - {{ todayStr }}</p>
      </div>
      <div class="header-actions">
        <button class="btn-refresh" @click="fetchData" :disabled="loading">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i> รีเฟรชข้อมูล
        </button>
      </div>
    </div>

    <div class="dashboard-content">
      <div v-if="loading" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i>
        <span>กำลังประมวลผลข้อมูล...</span>
      </div>

      <div v-else class="summary-table-container">
        <table class="summary-table">
          <thead>
            <tr>
              <th>พนักงาน</th>
              <th>Clock-in</th>
              <th>Clock-out</th>
              <th>สถานะ</th>
              <th>สถานที่</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in attendanceData" :key="item.user_id">
              <td class="col-user">
                <div class="user-info-cell">
                  <div class="emp-photo-wrapper">
                    <img v-if="item.photo_path" :src="mediaUrl(item.photo_path)" class="emp-photo" />
                    <div v-else class="emp-photo-placeholder">{{ item.first_name?.[0] || item.username?.[0] }}</div>
                  </div>
                  <div class="emp-text">
                    <div class="emp-name">{{ item.first_name }} {{ item.last_name }}</div>
                    <div class="emp-role">{{ item.job_title || 'No Position' }}</div>
                  </div>
                </div>
              </td>
              
              <td class="col-time">
                <div v-if="item.attendance?.check_in_time" class="time-wrap">
                  <span class="time-val">{{ formatTime(item.attendance.check_in_time) }}</span>
                  <span class="status-mini-label" :style="{ backgroundColor: getStatusBg(item.attendance.status), color: getStatusColor(item.attendance.status) }">
                    {{ formatStatusLabel(item.attendance.status, item.attendance.late_minutes) }}
                  </span>
                </div>
                <span v-else class="empty-val">—</span>
              </td>

              <td class="col-time">
                <div v-if="item.attendance?.actual_check_out" class="time-wrap">
                  <span class="time-val" :style="{ color: getCheckoutColor(item) }">
                    {{ formatTime(item.attendance.actual_check_out) }}
                  </span>
                  <span v-if="item.ot_request" class="status-mini-label ot-label">
                    OT {{ item.ot_request.total_hours }} hr ({{ item.ot_request.end_time }})
                  </span>
                </div>
                <span v-else class="empty-val">—</span>
              </td>

              <td class="col-status">
                <span v-if="item.attendance" class="status-pill" :class="item.attendance.status">
                  {{ item.attendance.status === 'present' ? 'Present' : 'Late' }}
                </span>
                <span v-else class="status-pill absent">Absent</span>
              </td>

              <td class="col-location">
                <span v-if="item.attendance?.site_name" class="location-badge">{{ item.attendance.site_name }}</span>
                <span v-else class="empty-val">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../../api'
import { mediaUrl } from '../../utils/mediaUrl'

const loading = ref(false)
const attendanceData = ref([])
const otRules = ref({})

const todayStr = computed(() => {
  return new Date().toLocaleDateString('th-TH', { 
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' 
  })
})

onMounted(async () => {
  await fetchData()
})

const fetchData = async () => {
  try {
    loading.value = true
    // 1. ดึงกฎเวลา
    const ruleRes = await api.get('/attendance/ot-rules')
    otRules.value = ruleRes.data
    
    // 2. ดึงข้อมูลพนักงานและการลงเวลาวันนี้
    const response = await api.get('/attendance/today')
    attendanceData.value = response.data
  } catch (error) {
    console.error("Error fetching today's attendance:", error)
  } finally {
    loading.value = false
  }
}

// --- Helpers (Reused from AttendancePanel) ---

const parseSafeDate = (dateStr) => {
  if (!dateStr) return null
  const t = dateStr.split(/[-T:.]/)
  if (t.length >= 5) return new Date(t[0], t[1] - 1, t[2], t[3], t[4], t[5] || 0)
  return new Date(dateStr)
}

const formatTime = (isoStr) => {
  if (!isoStr) return '—'
  const date = parseSafeDate(isoStr)
  if (!date || isNaN(date.getTime())) return '—'
  return date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false })
}

const getStatusColor = (status) => {
  if (status === 'late_t1') return '#854d0e'
  if (status === 'late_t2') return '#9a3412'
  if (status === 'late_t3') return '#991b1b'
  return '#10b981'
}

const getStatusBg = (status) => {
  if (status === 'late_t1') return '#fef9c3'
  if (status === 'late_t2') return '#ffedd5'
  if (status === 'late_t3') return '#fee2e2'
  return '#ecfdf5'
}

const formatStatusLabel = (status, lateMins = 0) => {
  if (status?.startsWith('late')) return `Late ${lateMins} m`
  if (status === 'none' || !status) return ''
  return 'On-Time'
}

const getCheckoutColor = (item) => {
  const actualStr = item.attendance?.actual_check_out
  if (!actualStr || !otRules.value.check_out_time) return '#1e293b'
  
  const actual = parseSafeDate(actualStr)
  const actualTime = actual.getHours() * 60 + actual.getMinutes()
  
  if (item.ot_request) {
    const [otH, otM] = item.ot_request.end_time.split(':').map(Number)
    const otEndTime = otH * 60 + otM
    return actualTime < otEndTime ? '#ef4444' : '#3b82f6'
  }

  const [stdH, stdM] = otRules.value.check_out_time.split(':').map(Number)
  const stdEndTime = stdH * 60 + stdM
  return actualTime < stdEndTime ? '#ef4444' : '#10b981'
}
</script>

<style scoped>
.attendance-dashboard {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f1f5f9;
}

.dashboard-header h2 {
  font-size: 1.6rem;
  color: #1e293b;
  margin: 0 0 4px 0;
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
  font-weight: 500;
}

.btn-refresh {
  background: white;
  border: 1px solid #e2e8f0;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 700;
  color: #1e293b;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-refresh:hover:not(:disabled) {
  border-color: #3b82f6;
  color: #3b82f6;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 0;
  color: #64748b;
  gap: 16px;
}

.loading-state i {
  font-size: 2.5rem;
  color: #3b82f6;
}

/* Table Styles */
.summary-table-container {
  background: white;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.summary-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.summary-table th {
  background: #f8fafc;
  padding: 16px;
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  color: #64748b;
  border-bottom: 1px solid #e2e8f0;
  letter-spacing: 0.05em;
}

.summary-table td {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

/* User Column */
.user-info-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.emp-photo-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  background: #f1f5f9;
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
  background: #e2e8f0;
  color: #64748b;
  font-weight: 800;
}

.emp-name {
  font-weight: 700;
  color: #1e293b;
  font-size: 0.95rem;
}

.emp-role {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
}

/* Time Columns */
.time-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.time-val {
  font-weight: 800;
  font-size: 1.05rem;
  color: #1e293b;
}

.status-mini-label {
  font-size: 0.6rem;
  font-weight: 800;
  padding: 1px 6px;
  border-radius: 4px;
  align-self: flex-start;
  text-transform: uppercase;
}

.ot-label {
  background-color: #e0e7ff;
  color: #4338ca;
}

/* Status Column */
.status-pill {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.status-pill.present { background: #ecfdf5; color: #10b981; }
.status-pill.late_t1, .status-pill.late_t2, .status-pill.late_t3 { background: #fff7ed; color: #f97316; }
.status-pill.absent { background: #fef2f2; color: #ef4444; }

/* Location Badge */
.location-badge {
  background: #f1f5f9;
  color: #475569;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
}

.empty-val {
  color: #cbd5e1;
}

@media (max-width: 768px) {
  .summary-table th:nth-child(4),
  .summary-table td:nth-child(4),
  .summary-table th:nth-child(5),
  .summary-table td:nth-child(5) {
    display: none;
  }
}
</style>
