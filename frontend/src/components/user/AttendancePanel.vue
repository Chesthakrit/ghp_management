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
          <!-- Standard ON-SITE Button only -->
          <button class="btn-onsite-square" @click="handleOnSiteCheckin">
            <i class="fas fa-map-marker-alt"></i>
            <span>ON-SITE</span>
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
            <tr v-for="day in weekDays" :key="day.fullDate">
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

let timerInterval = null

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

.btn-onsite-square { width: 90px; height: 90px; display: flex; flex-direction: column; align-items: center; justify-content: center; background-color: #f39c12; color: white; border: none; border-radius: 12px; cursor: pointer; transition: all 0.2s ease; box-shadow: 0 4px 10px rgba(243, 156, 18, 0.3); padding: 0; }
.btn-onsite-square i { font-size: 1.8rem; margin-bottom: 5px; }
.btn-onsite-square span { font-size: 0.75rem; font-weight: 800; }
.btn-onsite-square:hover { background-color: #e67e22; transform: translateY(-2px); }

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

@media (max-width: 480px) {
  .header-titles { min-width: 150px; }
  .time-display-large { font-size: 2rem; }
  .btn-onsite-square { width: 75px; height: 75px; }
}
</style>
