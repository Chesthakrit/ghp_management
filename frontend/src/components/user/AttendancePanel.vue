<template>
  <div class="attendance-panel-container">
    <div class="attendance-header">
      
      <!-- Title and Time Section -->
      <div class="header-titles">
        <h1>Attendance</h1>
        <div class="time-display-large">{{ currentTime }}</div>
        <div class="date-text-small">{{ currentDate }}</div>
      </div>
      
      <!-- Actions Section -->
      <div class="header-actions">
        <div v-if="!isLoading" class="salary-type-badge" :class="salaryType">
          {{ salaryType === 'monthly' ? 'Monthly Paid' : 'Daily Paid' }}
        </div>
        
        <div class="action-group">
          <button class="btn-action-square btn-onsite" @click="handleOnSiteCheckin">
            <i class="fas fa-map-marker-alt"></i>
            <span>ON-SITE</span>
          </button>
          
          <button class="btn-action-square btn-user" @click="handleCheckinUser">
            <i class="fas fa-user-clock"></i>
            <span>BY USER</span>
          </button>
          
          <button class="btn-action-square btn-factory" @click="handleCheckinFactory">
            <i class="fas fa-industry"></i>
            <span>FACTORY</span>
          </button>
          
          <button class="btn-action-square btn-ot" @click="handleOTRequest">
            <i class="fas fa-business-time"></i>
            <span>OT REQ</span>
          </button>
        </div>
      </div>

    </div>

    <div class="attendance-body">
      <!-- Week Navigation -->
      <div class="week-navigation">
        <button class="nav-btn" @click="changeWeek(-1)" :disabled="isAtHireDate">
          <i class="fas fa-chevron-left"></i>
        </button>
        
        <div class="nav-selectors">
          <select v-model="selectedMonth" @change="onMonthYearChange" class="nav-select">
            <option v-for="(m, idx) in months" :key="idx" :value="idx">{{ m }}</option>
          </select>
          <select v-model="selectedYear" @change="onMonthYearChange" class="nav-select">
            <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
          </select>
          <button class="today-btn" @click="goToCurrentWeek">Today</button>
        </div>

        <div class="current-week-range">
          {{ weekDays[0]?.dateStr }} - {{ weekDays[6]?.dateStr }}
        </div>

        <button class="nav-btn" @click="changeWeek(1)" :disabled="isFutureWeek">
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>

      <!-- Attendance Table -->
      <div class="table-container">
        <table class="attendance-table">
          <thead>
            <tr>
              <th>Day / Date</th>
              <th>Clock-in</th>
              <th>Clock-out</th>
              <th>OT (hrs.)</th>
              <th>Location</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="day in weekDays" :key="day.fullDate" :class="{ 'current-day': isToday(day.fullDate) }">
              <td class="col-date">
                <span class="day-label">{{ day.dayName }}</span>
                <span class="date-label">{{ day.dateStr }}</span>
              </td>
              <td class="col-time">{{ day.clockIn }}</td>
              <td class="col-time">{{ day.clockOut }}</td>
              <td class="col-ot">{{ day.ot }}</td>
              <td class="col-location">
                <span v-if="day.location !== '—'" class="location-badge onsite">{{ day.location }}</span>
                <span v-else>—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- User Check-in Modal -->
    <div v-if="isUserCheckinModalOpen" class="modal-overlay" @click="isUserCheckinModalOpen = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3><i class="fas fa-user-clock"></i> User Check-in / Out</h3>
          <button class="close-btn" @click="isUserCheckinModalOpen = false"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body">
          <p class="modal-desc">กรุณาเลือกรายการบันทึกเวลาของคุณ</p>
          <div class="modal-actions-row">
            <button class="action-btn btn-checkin" @click="performUserCheckin">
              <i class="fas fa-sign-in-alt"></i>
              <span>Clock IN</span>
            </button>
            <button class="action-btn btn-checkout" @click="performUserCheckout">
              <i class="fas fa-sign-out-alt"></i>
              <span>Clock OUT</span>
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import api from '../../api'

const props = defineProps(['userId'])

// Core States
const currentTime = ref('00:00:00')
const currentDate = ref('')
const salaryType = ref('')
const hireDateStr = ref('') 
const isLoading = ref(true)
const baseDate = ref(new Date())
const weekDays = ref([])
const historyLogs = ref([])

// Constants
const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
const selectedMonth = ref(new Date().getMonth())
const selectedYear = ref(new Date().getFullYear())

const isUserCheckinModalOpen = ref(false)

let timerInterval = null

// Helper
const isToday = (dateStr) => {
  const today = new Date()
  today.setMinutes(today.getMinutes() - today.getTimezoneOffset()) // Handle local timezone issues
  return dateStr === today.toISOString().split('T')[0]
}

// Computed: Dropdown Years
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  const startYear = hireDateStr.value ? new Date(hireDateStr.value).getFullYear() : currentYear
  const years = []
  for (let y = currentYear; y >= startYear; y--) { years.push(y) }
  return years
})

// Computed: Navigation Constraints
const isAtHireDate = computed(() => {
  if (!hireDateStr.value || weekDays.value.length === 0) return false
  const mondayOfView = new Date(weekDays.value[0].fullDate)
  const hireDate = new Date(hireDateStr.value)
  const hireMonday = new Date(hireDate)
  const dayOfWeek = hireDate.getDay()
  const diffToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek
  hireMonday.setDate(hireDate.getDate() + diffToMonday)
  hireMonday.setHours(0,0,0,0)
  return mondayOfView <= hireMonday
})

const isFutureWeek = computed(() => {
  if (weekDays.value.length === 0) return false
  const today = new Date()
  today.setHours(0,0,0,0)
  const mondayOfView = new Date(weekDays.value[0].fullDate)
  const tDayOfWeek = today.getDay()
  const tDiffToMonday = tDayOfWeek === 0 ? -6 : 1 - tDayOfWeek
  const todayMonday = new Date(today)
  todayMonday.setDate(today.getDate() + tDiffToMonday)
  return mondayOfView >= todayMonday
})

// Methods: Week Generation
const generateWeek = (date = new Date()) => {
  const days = []
  const dayOfWeek = date.getDay()
  const diffToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek
  const monday = new Date(date)
  monday.setDate(date.getDate() + diffToMonday)
  
  for (let i = 0; i < 7; i++) {
    const day = new Date(monday)
    day.setDate(monday.getDate() + i)
    const logDate = day.toISOString().split('T')[0]
    const log = historyLogs.value.find(l => l.date === logDate)
    
    days.push({
      dateStr: day.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
      dayName: day.toLocaleDateString('en-US', { weekday: 'short' }),
      fullDate: logDate,
      clockIn: log?.check_in_time ? formatTime(log.check_in_time) : '—',
      clockOut: log?.check_out_time ? formatTime(log.check_out_time) : '—',
      ot: log ? "0.0" : "0.0",
      location: log ? log.site_name : '—'
    })
  }
  weekDays.value = days
}

const formatTime = (isoStr) => {
  if (!isoStr) return '—'
  return new Date(isoStr).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
}

// API Calls
const fetchUserData = async () => {
  try {
    const endpoint = props.userId ? `/users/${props.userId}` : '/users/me'
    const res = await api.get(endpoint)
    if (res.data?.employee_profile) {
      salaryType.value = res.data.employee_profile.salary_type || 'monthly'
      hireDateStr.value = res.data.employee_profile.hire_date || ''
    }
  } catch (e) { console.error(e) }
}

const fetchMyAttendance = async () => {
  try {
    const endpoint = props.userId ? `/attendance/user/${props.userId}` : '/attendance/me'
    const res = await api.get(endpoint)
    historyLogs.value = res.data || []
    generateWeek(baseDate.value)
  } catch (e) { console.error(e) }
}

// Navigation
const changeWeek = (diff) => {
  const d = new Date(baseDate.value)
  d.setDate(d.getDate() + (diff * 7))
  baseDate.value = d
  generateWeek(d)
  selectedMonth.value = d.getMonth()
  selectedYear.value = d.getFullYear()
}

const onMonthYearChange = () => {
  const d = new Date(selectedYear.value, selectedMonth.value, 1)
  baseDate.value = d
  generateWeek(d)
}

const goToCurrentWeek = () => {
  const now = new Date()
  baseDate.value = now
  generateWeek(now)
  selectedMonth.value = now.getMonth()
  selectedYear.value = now.getFullYear()
}

const updateClock = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('en-US', { hour12: false })
  currentDate.value = now.toLocaleDateString('en-US', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' })
}

const handleOnSiteCheckin = () => {
  alert("Live Check-in feature will be implemented soon.")
}

const handleCheckinUser = () => {
  // alert("Check-in by User feature will be implemented soon.")
  isUserCheckinModalOpen.value = true
}

const performUserCheckin = () => {
  alert("Simulating Check-In...")
  isUserCheckinModalOpen.value = false
}

const performUserCheckout = () => {
  alert("Simulating Check-Out...")
  isUserCheckinModalOpen.value = false
}

const handleCheckinFactory = () => {
  alert("Check-in on Factory feature will be implemented soon.")
}

const handleOTRequest = () => {
  alert("OT Request feature will be implemented soon.")
}

// Lifecycle
onMounted(async () => {
  isLoading.value = true
  updateClock()
  timerInterval = setInterval(updateClock, 1000)
  await fetchUserData()
  await fetchMyAttendance()
  isLoading.value = false
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})
</script>

<style scoped>
.attendance-panel-container { padding: 20px; }

.attendance-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 2px solid #ecf0f1;
}

.header-titles { display: flex; flex-direction: column; align-items: center; text-align: center; min-width: 200px; }

.attendance-header h1 { margin: 0 0 5px 0; font-size: 1.6rem; color: #2c3e50; text-transform: uppercase; letter-spacing: 2px; font-weight: 700; }

.time-display-large { font-size: 2.8rem; font-weight: 800; font-family: 'Courier New', Courier, monospace; color: #2ecc71; line-height: 1; margin: 5px 0; letter-spacing: -1px; }

.date-text-small { font-size: 0.85rem; color: #95a5a6; margin-top: 2px; font-weight: 500; }

.header-actions { display: flex; flex-direction: column; align-items: flex-end; gap: 8px; }

.salary-type-badge { font-size: 0.7rem; font-weight: 800; text-transform: uppercase; padding: 4px 10px; border-radius: 20px; letter-spacing: 0.5px; }
.salary-type-badge.monthly { background-color: #e8f4fd; color: #3498db; border: 1px solid #3498db; }
.salary-type-badge.daily { background-color: #fef9e7; color: #f1c40f; border: 1px solid #f1c40f; }

.action-group { display: flex; gap: 12px; margin-top: 5px; }

.btn-action-square { width: 85px; height: 85px; display: flex; flex-direction: column; align-items: center; justify-content: center; background-color: #ffffff; color: #475569; border: 1px solid #e2e8f0; border-radius: 14px; cursor: pointer; transition: all 0.2s ease; padding: 0; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
.btn-action-square i { font-size: 1.5rem; margin-bottom: 8px; transition: transform 0.2s; }
.btn-action-square span { font-size: 0.65rem; font-weight: 800; text-transform: uppercase; text-align: center; line-height: 1.1; padding: 0 4px; letter-spacing: 0.02em; }
.btn-action-square:hover { transform: translateY(-3px); box-shadow: 0 8px 16px rgba(0,0,0,0.06); border-color: #cbd5e1; }
.btn-action-square:hover i { transform: scale(1.1); }

/* Theme Accents */
.btn-onsite { border-bottom: 3px solid #3b82f6; }
.btn-onsite i { color: #3b82f6; }
.btn-onsite:hover { background-color: #eff6ff; color: #1e40af; border-bottom-color: #2563eb; }

.btn-factory { border-bottom: 3px solid #f59e0b; }
.btn-factory i { color: #f59e0b; }
.btn-factory:hover { background-color: #fffbeb; color: #b45309; border-bottom-color: #d97706; }

.btn-user { border-bottom: 3px solid #10b981; }
.btn-user i { color: #10b981; }
.btn-user:hover { background-color: #ecfdf5; color: #047857; border-bottom-color: #059669; }

.btn-ot { border-bottom: 3px solid #8b5cf6; }
.btn-ot i { color: #8b5cf6; }
.btn-ot:hover { background-color: #f5f3ff; color: #5b21b6; border-bottom-color: #7c3aed; }

.attendance-body { margin-top: 1rem; }
.week-navigation { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; background-color: #fcfcfc; padding: 10px 15px; border-radius: 12px; border: 1px solid #f1f1f1; gap: 10px; }
.nav-selectors { display: flex; gap: 8px; }
.nav-select { padding: 6px 12px; border-radius: 8px; border: 1px solid #e2e8f0; background: white; font-size: 0.85rem; font-weight: 600; color: #34495e; outline: none; cursor: pointer; }
.today-btn { background: #f8fafc; border: 1px solid #e2e8f0; padding: 6px 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 700; color: #3498db; cursor: pointer; transition: 0.2s; }
.today-btn:hover { background: #3498db; color: white; }
.current-week-range { font-weight: 700; font-size: 0.95rem; color: #34495e; min-width: 250px; text-align: center; }
.nav-btn { background: white; border: 1px solid #e2e8f0; padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; color: #2c3e50; cursor: pointer; transition: 0.2s; display: flex; align-items: center; }
.nav-btn:hover:not(:disabled) { border-color: #3498db; color: #3498db; }
.nav-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.table-container { overflow-x: auto; border-radius: 12px; background: white; border: 1px solid #f1f1f1; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03); }
.attendance-table { width: 100%; border-collapse: collapse; text-align: left; }
.attendance-table th { background: #f8fafc; color: #7f8c8d; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; padding: 16px; border-bottom: 2px solid #f1f1f1; }
.attendance-table td { padding: 16px; border-bottom: 1px solid #f9f9f9; font-size: 0.95rem; color: #2c3e50; }
.col-date { display: flex; flex-direction: column; }
.day-label { font-weight: 700; color: #34495e; }
.date-label { font-size: 0.8rem; color: #95a5a6; }
.col-time { font-weight: 600; color: #3498db; }
.col-ot { font-weight: 700; color: #e67e22; }
.location-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
.location-badge.onsite { background: #e8f8f5; color: #1abc9c; }

/* Highlight Current Day */
.attendance-table tr.current-day {
  background-color: #eff6ff; 
}
.attendance-table tr.current-day td:first-child {
  border-left: 5px solid #3b82f6;
  padding-left: 11px; /* Adjust padding to compensate for the border */
}
.attendance-table tr.current-day td {
  border-bottom: 1px solid #bfdbfe;
}
.attendance-table tr.current-day .day-label {
  color: #1e3a8a;
}
.attendance-table tr.current-day .date-label {
  color: #3b82f6;
  font-weight: 700;
}

@media (max-width: 480px) {
  .attendance-header { flex-direction: column; align-items: center; gap: 20px; }
  .header-actions { align-items: center; width: 100%; }
  .action-group { width: 100%; justify-content: center; gap: 8px; flex-wrap: wrap; }
  .btn-action-square { width: 22%; max-width: 85px; height: 75px; }
  .header-titles { min-width: 150px; }
  .time-display-large { font-size: 2rem; }
}

/* Modal Styles */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}

.modal-content {
  background: white; border-radius: 20px; width: 90%; max-width: 400px;
  box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
  overflow: hidden; animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.modal-header {
  padding: 20px 24px; border-bottom: 1px solid #f1f5f9;
  display: flex; justify-content: space-between; align-items: center;
  background: #f8fafc;
}

.modal-header h3 { margin: 0; font-size: 1.15rem; color: #1e293b; display: flex; align-items: center; gap: 10px; }
.modal-header i { color: #3b82f6; }
.close-btn { background: transparent; border: none; font-size: 1.2rem; color: #94a3b8; cursor: pointer; transition: 0.2s; }
.close-btn:hover { color: #ef4444; transform: scale(1.1); }

.modal-body { padding: 24px; }
.modal-desc { margin: 0 0 20px 0; color: #64748b; font-size: 0.95rem; text-align: center; }

.modal-actions-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.action-btn {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 10px; padding: 20px; border-radius: 14px; border: none; cursor: pointer;
  transition: all 0.2s; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.85rem; color: white;
}

.action-btn i { font-size: 2rem; }

.btn-checkin { background: #10b981; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }
.btn-checkin:hover { background: #059669; transform: translateY(-3px); }

.btn-checkout { background: #ef4444; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3); }
.btn-checkout:hover { background: #dc2626; transform: translateY(-3px); }

</style>
