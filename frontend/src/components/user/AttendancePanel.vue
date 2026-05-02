<template>
  <div class="attendance-panel-container">
    <div class="attendance-header">
      
      <!-- [1] ส่วนหัวเรื่องและแสดงเวลาปัจจุบัน (Real-time Clock) -->
      <div class="header-titles">
        <h1>Attendance</h1>
        <div class="time-display-large">{{ currentTime }}</div> <!-- แสดงเวลา Live 24H -->
        <div class="date-text-small">{{ currentDate }}</div> <!-- แสดงวันที่ปัจจุบัน -->
      </div>
      
      <!-- [2] ส่วนปุ่ม Action หลัก (On-site, Factory, By User) -->
      <div class="header-actions">
        <!-- แสดงประเภทเงินเดือน (รายวัน/รายเดือน) -->
        <div v-if="!isLoading" class="salary-type-badge" :class="salaryType">
          {{ salaryType === 'monthly' ? 'Monthly Paid' : 'Daily Paid' }}
        </div>
        
        <div class="action-group">
          <!-- ปุ่มขอ OT: แสดงเฉพาะเมื่อดูประวัติของตัวเองเท่านั้น (ป้องกันแอดมินกดแทน) -->
          <button v-if="!props.userId" class="btn-action-square btn-ot" @click="handleOTRequest">
            <i class="fas fa-business-time"></i>
            <span>OT REQ</span>
          </button>
        </div>
      </div>

    </div>

    <div class="attendance-body">
      <!-- [3] ส่วนควบคุมการดูปฏิทิน (เลิกดูย้อนหลังรายอาทิตย์/เดือน/ปี) -->
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

      <!-- [4] ตารางแสดงประวัติการลงเวลา (Attendance Table) -->
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
            <!-- วนลูปแสดงข้อมูล 7 วันในสัปดาห์ที่เลือก -->
            <tr v-for="day in weekDays" :key="day.fullDate" :class="{ 'current-day': isToday(day.fullDate) }">
              <td class="col-date">
                <span class="day-label">{{ day.dayName }}</span>
                <span class="date-label">{{ day.dateStr }}</span>
              </td>
              <td class="col-time">
                <div v-if="day.clockIn !== '\u2014'" class="time-status-wrap">
                  <span class="clickable-time" :style="{ color: getStatusColor(day.status) }">
                    {{ day.clockIn }}
                  </span>
                  <span class="status-mini-label" :style="{ backgroundColor: getStatusBg(day.status), color: getStatusColor(day.status) }">
                    {{ formatStatusLabel(day.status, day.lateMinutes) }}
                  </span>
                </div>
                <span v-else class="empty-val">—</span>
              </td>
              <!-- แสดงเวลาออกงาน -->
              <td class="col-time">
                <div v-if="day.clockOut !== '\u2014'" class="time-status-wrap">
                  <span class="clickable-time" :style="{ color: getCheckoutColor(day) }">
                    {{ day.clockOut }}
                  </span>
                </div>
                <span v-else class="empty-val">—</span>
              </td>
              <!-- แสดงจำนวน OT ( hrs.) พร้อมสถานะและการแตะเพื่อดูรายละเอียด -->
              <td class="col-ot">
                <div v-if="day.otRequest" class="ot-info-wrap" @click="viewOTDetail(day.otRequest)">
                  <div class="ot-hours">{{ day.ot }} hrs.</div>
                  
                  <!-- สถานะการอนุมัติ -->
                  <span class="ot-status-badge" :class="day.otRequest.status">
                    {{ formatOtStatus(day.otRequest.status) }}
                  </span>
                </div>
                <span v-else class="empty-val">0.0</span>
              </td>
              <!-- แสดงชื่อสถานที่เช็คอิน -->
              <td class="col-location">
                <span v-if="day.location !== '—'" class="location-badge onsite">{{ day.location }}</span>
                <span v-else class="empty-val">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- [5] หน้าต่าง Modal ดูรูปภาพหลักฐานตอนลงเวลา -->
    <div v-if="isPreviewModalOpen" class="modal-overlay preview" @click="isPreviewModalOpen = false">
      <div class="modal-content preview-content" @click.stop>
        <div class="modal-header">
          <h3><i class="fas fa-camera"></i> {{ previewTitle }}</h3>
          <button class="close-btn" @click="isPreviewModalOpen = false"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body preview-body">
          <div v-if="previewImage" class="photo-frame">
            <img :src="previewImage" alt="Attendance Photo" class="preview-img" />
          </div>
          <div v-else class="no-photo">
            <i class="fas fa-image-slash"></i>
            <p>ไม่มีรูปถ่ายสำหรับรายการนี้</p>
          </div>
          <div class="photo-info">
            <span class="info-label">Timestamp:</span>
            <span class="info-value">{{ previewTimestamp }}</span>
          </div>
        </div>
      </div>
    </div>


    <!-- [7] หน้าต่าง Modal สำหรับขอโอที (OT Request) -->
    <OTRequestModal 
      :isOpen="isOTModalOpen" 
      :user="currentUser" 
      :attendanceLogs="historyLogs"
      @close="isOTModalOpen = false"
      @submitted="fetchMyAttendance"
    />

    <!-- [8] Popup แสดงรายละเอียด OT (OT Detail Modal) -->
    <div v-if="isOTDetailModalOpen" class="modal-overlay" @click="isOTDetailModalOpen = false">
      <div class="modal-content detail-modal" @click.stop>
        <div class="modal-header">
          <h3><i class="fas fa-info-circle"></i> OT Details</h3>
          <button class="close-btn" @click="isOTDetailModalOpen = false"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body" v-if="selectedOtDetail">
          <div class="detail-grid">
            <div class="detail-item">
              <label><i class="fas fa-calendar-alt"></i> Date</label>
              <div class="val">{{ formatDate(selectedOtDetail.request_date) }}</div>
            </div>
            <div class="detail-item">
              <label><i class="fas fa-signal"></i> Status</label>
              <div class="val">
                <span class="ot-status-badge" :class="selectedOtDetail.status">
                  {{ formatOtStatus(selectedOtDetail.status) }}
                </span>
              </div>
            </div>
            <div class="detail-item full">
              <label><i class="fas fa-clock"></i> Time Range</label>
              <div class="val highlight">
                {{ selectedOtDetail.start_time }} - {{ selectedOtDetail.end_time }}
              </div>
            </div>
            <div class="detail-item">
              <label><i class="fas fa-hourglass-start"></i> Standard OT</label>
              <div class="val">{{ selectedOtDetail.standard_hours }} hrs.</div>
            </div>
            <div class="detail-item">
              <label><i class="fas fa-star"></i> Special OT</label>
              <div class="val text-special">{{ selectedOtDetail.special_hours }} hrs.</div>
            </div>
            <div class="detail-item full total-row">
              <label><i class="fas fa-calculator"></i> Total Hours</label>
              <div class="val large">{{ selectedOtDetail.total_hours }} hrs.</div>
            </div>
            <div class="detail-item full" v-if="selectedOtDetail.reason">
              <label><i class="fas fa-comment-dots"></i> Reason</label>
              <div class="reason-box">{{ selectedOtDetail.reason }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import api from '../../api'
import OTRequestModal from './OTRequestModal.vue'

const props = defineProps(['userId'])

const currentTime = ref('00:00:00') // เวลาปัจจุบัน 24H
const currentDate = ref('')        // วันที่ปัจจุบัน
const salaryType = ref('')         // ประเภทเงินเดิอนพนักงาน
const hireDateStr = ref('')        // วันที่เริ่มงาน
const isLoading = ref(true)        // สถานะโหลดข้อมูล
const baseDate = ref(new Date())   // วันที่ฐาน
const weekDays = ref([])           
const historyLogs = ref([])        
const currentUser = ref(null)      

const isOTModalOpen  = ref(false)
const myOtRequests   = ref([]) // เก็บรายการ OT แยกต่างหาก

// สำหรับ Popup ดูรายละเอียด OT
const isOTDetailModalOpen = ref(false)
const selectedOtDetail    = ref(null)

const months        = ['January','February','March','April','May','June','July','August','September','October','November','December']
const selectedMonth = ref(new Date().getMonth())
const selectedYear  = ref(new Date().getFullYear())
const otRules       = ref({}) // เก็บกฎเวลาจาก Backend
let timerInterval   = null

// --- 5. การคำนวณอัตโนมัติ (Computed) ---
// สร้างรายการปีที่เลือกได้ในปฏิทิน
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  const startYear = hireDateStr.value ? new Date(hireDateStr.value).getFullYear() : currentYear
  const years = []
  for (let y = currentYear; y >= startYear; y--) { years.push(y) }
  return years
})

// เช็คว่าดูย้อนหลังไปถึงวันเริ่มงานหรือยัง (ถ้าถึงแล้วให้กดปุ่มย้อนหลังไม่ได้)
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

// เช็คว่าเป็นสัปดาห์ในอนาคตหรือไม่ (ห้ามดูอนาคต)
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

// ─── Helper Methods ───────────────────────────────────────────────────────────

/**
 * ฟังก์ชันช่วยสร้าง Date Object แบบปลอดภัย สำหรับแสดงผลเวลา
 */
const parseSafeDate = (dateStr) => {
  if (!dateStr) return null
  try {
    const t = dateStr.split(/[-T:.]/)
    if (t.length >= 5) {
      return new Date(t[0], t[1] - 1, t[2], t[3], t[4], t[5] || 0)
    }
    return new Date(dateStr)
  } catch (e) {
    return new Date()
  }
}

// ตรวจสอบว่าเป็นวันนี้หรือไม่
const isToday = (dateStr) => {
  const today = new Date()
  // จัดการเรื่อง Timezone Offset ของ JS Date
  today.setMinutes(today.getMinutes() - today.getTimezoneOffset())
  return dateStr === today.toISOString().split('T')[0]
}

// แปลงเวลาให้เป็น 24H (HH:mm)
const formatTime = (isoStr) => {
  if (!isoStr) return '—'
  const date = parseSafeDate(isoStr)
  if (!date || isNaN(date.getTime())) return '—'
  return date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false })
}

// แปลงวันที่และเวลาแบบเต็ม (สำหรับดูในรูปถ่าย)
const formatFullTime = (isoStr) => {
  if (!isoStr) return ''
  const date = parseSafeDate(isoStr)
  if (!date || isNaN(date.getTime())) return ''
  return date.toLocaleString('en-GB', { 
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit', second: '2-digit', 
    hour12: false 
  })
}

// อัปเดตนาฬิกาวิ่งสด (Live Clock)
const updateClock = () => {
  const now = new Date()
  // ใช้มาตรฐาน en-GB เเพื่อให้ได้รูปแบบ 24H สากล
  currentTime.value = now.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })
  currentDate.value = now.toLocaleDateString('en-US', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' })
}

// --- 7. ลอจิกการแสดงสถานะ (UI Display Logic) ---
// (ลบฟังก์ชัน calculateStatus ทิ้ง เพราะเราใช้สถานะสำเร็จรูปจาก Database แทนแล้ว)

// คืนค่ารหัสสีตามสถานะ
const getStatusColor = (status) => {
  if (status === 'late_t1') return '#854d0e' // Yellow-Dark
  if (status === 'late_t2') return '#9a3412' // Orange-Dark
  if (status === 'late_t3') return '#991b1b' // Red-Dark
  return '#10b981' // Green
}

// คืนค่าพื้นหลังป้ายตามสถานะ
const getStatusBg = (status) => {
  if (status === 'late_t1') return '#fef9c3'
  if (status === 'late_t2') return '#ffedd5'
  if (status === 'late_t3') return '#fee2e2'
  return '#ecfdf5'
}

const formatOtStatus = (status) => {
  if (status === 'pending') return 'Pending'
  if (status === 'approved') return 'Approved'
  if (status === 'rejected') return 'Rejected'
  return status
}

const viewOTDetail = (ot) => {
  selectedOtDetail.value = ot
  isOTDetailModalOpen.value = true
}

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

// แปลงรหัสสถานะเป็นชื่อแสดงผล
const formatStatusLabel = (status, lateMins = 0) => {
  if (status === 'late_t1' || status === 'late_t2' || status === 'late_t3') {
    return `Late ${lateMins} min`
  }
  if (status === 'none') return ''
  return 'On-Time'
}

// --- 7.1 ลอจิกการแสดงสีเวลาออก (Checkout Color Logic) ---
const getCheckoutColor = (day) => {
  if (!day.actualCheckOut || !otRules.value.check_out_time) return '#1e293b'
  
  const actual = parseSafeDate(day.actualCheckOut)
  if (!actual) return '#1e293b'

  const actualTime = actual.getHours() * 60 + actual.getMinutes()
  
  // 1. ถ้ามีการขอโอที
  if (day.otRequest) {
    const [otH, otM] = day.otRequest.end_time.split(':').map(Number)
    const otEndTime = otH * 60 + otM
    
    // ถ้าออกก่อนเวลาโอทีที่ขอ -> แดง
    if (actualTime < otEndTime) return '#ef4444'
    // ถ้าออกตามสั่งหรือหลัง -> น้ำเงิน
    return '#3b82f6'
  }

  // 2. ถ้าไม่มีโอที
  const [stdH, stdM] = otRules.value.check_out_time.split(':').map(Number)
  const stdEndTime = stdH * 60 + stdM
  
  // ถ้าออกก่อนเวลาปกติ -> แดง
  if (actualTime < stdEndTime) return '#ef4444'
  // ถ้าออกหลังเวลาปกติ -> เขียว
  return '#10b981'
}

// สร้างข้อมูลจำลอง 7 วันในสัปดาห์ปัจจุบัน
const generateWeek = (date = new Date()) => {
  const days = []
  const dayOfWeek = date.getDay()
  // หาวันจันทร์ของสัปดาห์ที่กำลังเลือกดู
  const diffToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek
  const monday = new Date(date)
  monday.setDate(date.getDate() + diffToMonday)
  
  for (let i = 0; i < 7; i++) {
    const day = new Date(monday)
    day.setDate(monday.getDate() + i)
    // สร้างวันที่แบบ YYYY-MM-DD ตามเวลาท้องถิ่น (ป้องกันบั๊ก Timezone)
    const y = day.getFullYear()
    const m = String(day.getMonth() + 1).padStart(2, '0')
    const d = String(day.getDate()).padStart(2, '0')
    const logDate = `${y}-${m}-${d}`

    const log = historyLogs.value.find(l => String(l.date).substring(0, 10) === logDate)
    
    // ค้นหา OT (หาใน log ก่อน ถ้าไม่มีให้หาในรายการ OT แยก)
    // ตัดเอาเฉพาะ YYYY-MM-DD มาเทียบเพื่อป้องกันเรื่องเวลาแฝง
    const otReq = (log?.ot_request) || myOtRequests.value.find(r => String(r.request_date).substring(0, 10) === logDate)
    
    days.push({
      dateStr:     day.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
      dayName:     day.toLocaleDateString('en-US', { weekday: 'short' }),
      fullDate:    logDate,
      clockIn:     log?.check_in_time  ? formatTime(log.check_in_time)  : '—',
      clockOut:    log?.actual_check_out ? formatTime(log.actual_check_out) : '—', // แสดงเวลาจริง
      actualCheckOut: log?.actual_check_out,
      otRequest:   otReq,
      status:      log?.status       || 'none',
      lateMinutes: log?.late_minutes || 0,
      ot:          otReq ? otReq.total_hours.toFixed(1) : '0.0',
      location:    log?.site_name    || '—',
    })
  }
  weekDays.value = days
}

// ดึงโปรไฟล์พนักงาน (เพื่อเช็คประเภทเงินเดือนและวันเริ่มงาน)
const fetchUserData = async () => {
  try {
    const endpoint = props.userId ? `/users/${props.userId}` : '/users/me'
    const res = await api.get(endpoint)
    const u = res.data
    currentUser.value = u

    if (u.employee_profile) {
      salaryType.value = u.employee_profile.salary_type || 'monthly'
      hireDateStr.value = u.employee_profile.hire_date || ''
    }
  } catch (e) { console.error(e) }
}


// ดึงประวัติการมาทำงานจริงจาก Database
const fetchMyAttendance = async () => {
  try {
    // ดึงกฎเวลาก่อนเพื่อใช้เปรียบเทียบ
    const ruleRes = await api.get('/attendance/ot-rules')
    otRules.value = ruleRes.data

    const endpoint = props.userId ? `/attendance/user/${props.userId}` : '/attendance/me'
    const res = await api.get(endpoint)
    historyLogs.value = res.data || []

    // ดึงรายการ OT แยกมาด้วย
    const otEndpoint = props.userId ? `/attendance/user/${props.userId}/ot-requests` : '/attendance/me/ot-requests'
    const otRes = await api.get(otEndpoint)
    myOtRequests.value = otRes.data || []

    generateWeek(baseDate.value)
  } catch (e) { console.error(e) }
}

// --- 8. ฟังก์ชันจัดการหน้าจอ (UI Interactions) ---
// เปลี่ยนอาทิตย์
const changeWeek = (diff) => {
  const d = new Date(baseDate.value)
  d.setDate(d.getDate() + (diff * 7))
  baseDate.value = d
  generateWeek(d)
  selectedMonth.value = d.getMonth()
  selectedYear.value = d.getFullYear()
}

// เมื่อเลือกเดือนหรือปีใน Dropdown
const onMonthYearChange = () => {
  const d = new Date(selectedYear.value, selectedMonth.value, 1)
  baseDate.value = d
  generateWeek(d)
}

// กลับมาดูอาทิตย์ปัจจุบันที่มี "วันนี้" อยู่
const goToCurrentWeek = () => {
  const now = new Date()
  baseDate.value = now
  generateWeek(now)
  selectedMonth.value = now.getMonth()
  selectedYear.value = now.getFullYear()
}


const handleOTRequest = () => { isOTModalOpen.value = true }


// --- 10. วงจรชีวิตของคอมโพเนนต์ (Lifecycle Hooks) ---
onMounted(async () => {
  isLoading.value = true
  updateClock()
  timerInterval = setInterval(updateClock, 1000) // สั่งให้นาฬิกาเดินทุกวินาที
  await fetchUserData()
  await fetchMyAttendance()
  isLoading.value = false
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval) // เคลียร์นาฬิกาเมื่อปิดหน้านี้เพื่อไม่ให้เปลืองทรัพยากร
})
</script>

<style scoped>
/* ────────── สไตล์ตกแต่งหน้าจอ (UI/UX Styling) ────────── */
.attendance-panel-container { padding: 20px; }

/* 1. Header Section - ส่วนหัวและนาฬิกาประจำโรงงาน */
.attendance-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 2px solid #ecf0f1;
}

.header-titles { display: flex; flex-direction: column; align-items: center; text-align: center; min-width: 200px; }
.attendance-header h1 { margin: 0 0 5px 0; font-size: 1.6rem; color: #2c3e50; text-transform: uppercase; letter-spacing: 2px; font-weight: 700; }
.time-display-large { font-size: 2.8rem; font-weight: 800; font-family: 'Courier New', Courier, monospace; color: #2ecc71; line-height: 1; margin: 5px 0; letter-spacing: -1px; }
.date-text-small { font-size: 0.85rem; color: #95a5a6; margin-top: 2px; font-weight: 500; }

/* ส่วนแสดงสถานะเงินเดือนและปุ่ม Action */
.header-actions { display: flex; flex-direction: column; align-items: flex-end; gap: 8px; }
.salary-type-badge { font-size: 0.7rem; font-weight: 800; text-transform: uppercase; padding: 4px 10px; border-radius: 20px; letter-spacing: 0.5px; }
.salary-type-badge.monthly { background-color: #e8f4fd; color: #3498db; border: 1px solid #3498db; }
.salary-type-badge.daily { background-color: #fef9e7; color: #f1c40f; border: 1px solid #f1c40f; }

.action-group { display: flex; gap: 12px; margin-top: 5px; }
.btn-action-square { width: 85px; height: 85px; display: flex; flex-direction: column; align-items: center; justify-content: center; background-color: #ffffff; color: #475569; border: 1px solid #e2e8f0; border-radius: 14px; cursor: pointer; transition: all 0.2s ease; padding: 0; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
.btn-action-square i { font-size: 1.5rem; margin-bottom: 8px; transition: transform 0.2s; }
.btn-action-square span { font-size: 0.65rem; font-weight: 800; text-transform: uppercase; text-align: center; line-height: 1.1; padding: 0 4px; letter-spacing: 0.02em; }
.btn-action-square:hover { transform: translateY(-3px); box-shadow: 0 8px 16px rgba(0,0,0,0.06); border-color: #cbd5e1; }

/* สีพื้นหลังของขอบด้านล่างปุ่มแยกตามประเภท */
.btn-onsite { border-bottom: 3px solid #3b82f6; }
.btn-onsite i { color: #3b82f6; }
.btn-factory { border-bottom: 3px solid #f59e0b; }
.btn-factory i { color: #f59e0b; }
.btn-user { border-bottom: 3px solid #10b981; }
.btn-user i { color: #10b981; }
.btn-ot { border-bottom: 3px solid #8b5cf6; }
.btn-ot i { color: #8b5cf6; }

/* 2. Navigation Section - ส่วนควบคุมอาทิตย์ */
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

/* 3. Table Section - สไตล์ตารางประวัติ */
.table-container { overflow-x: auto; border-radius: 12px; background: white; border: 1px solid #f1f1f1; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03); }
.attendance-table { width: 100%; border-collapse: collapse; text-align: left; }
.attendance-table th { background: #fafafa; color: #64748b; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; padding: 16px; border-bottom: 2px solid #f1f5f9; letter-spacing: 0.05em; }
.attendance-table td { padding: 12px 16px; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; color: #1e293b; vertical-align: middle; }

.col-date { display: flex; flex-direction: column; }
.day-label { font-weight: 800; color: #1a2a3a; font-size: 0.95rem; }
.date-label { font-size: 0.75rem; color: #94a3b8; font-weight: 500; }

/* เลย์เอาต์เวลาและสเตตัส (ยัดรวมในกระเป๋าเดียวกัน) */
.time-status-wrap { display: flex; flex-direction: column; gap: 4px; }
.status-mini-label { 
  font-size: 0.55rem; 
  font-weight: 800; 
  text-transform: uppercase; 
  padding: 1px 5px; 
  border-radius: 4px; 
  align-self: flex-start;
  letter-spacing: 0.01em;
}

.col-time { font-weight: 700; }
.col-ot { font-weight: 800; color: #1a2a3a; }
.empty-val { color: #cbd5e1; font-weight: 400; }

.location-badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; }
.location-badge.onsite { background: #f1f5f9; color: #1a2a3a; border: 1px solid #e2e8f0; }

.clickable-time { text-decoration: none; cursor: pointer; transition: 0.2s; font-weight: 800; font-size: 1.05rem; }
.clickable-time:hover { opacity: 0.7; }

/* เฉดสีไฮไลท์สำหรับ "วันนี้" */
.attendance-table tr.current-day { background-color: #eff6ff; }
.attendance-table tr.current-day td:first-child { border-left: 5px solid #3b82f6; padding-left: 11px; }
.attendance-table tr.current-day .date-label { color: #3b82f6; font-weight: 700; }

/* 4. Modal Base Styles - มาตรฐานหน้าต่างป๊อปอัพ */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal-content { background: white; border-radius: 20px; width: 90%; max-width: 400px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); overflow: hidden; animation: slideUp 0.3s ease; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px) scale(0.95); } to { opacity: 1; transform: translateY(0) scale(1); } }

.modal-header { padding: 20px 24px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; }
.modal-header h3 { margin: 0; font-size: 1.15rem; color: #1e293b; display: flex; align-items: center; gap: 10px; }
.close-btn { background: transparent; border: none; font-size: 1.2rem; color: #94a3b8; cursor: pointer; transition: 0.2s; }
.modal-body { padding: 24px; }

/* 5. Check-in Modal Elements - ตกแต่งหน้าต่างลงเวลา */
.checkin-form { margin-bottom: 24px; }
.form-label { display: block; font-size: 0.85rem; font-weight: 700; color: #64748b; margin-bottom: 10px; text-transform: uppercase; }
.location-tabs { display: flex; background: #f1f5f9; border-radius: 12px; overflow: hidden; padding: 4px; }
.loc-tab { flex: 1; padding: 12px 0; font-size: 0.95rem; font-weight: 700; color: #64748b; background: transparent; border: none; cursor: pointer; }
.loc-tab.active { background: white; color: #1e293b; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-radius: 8px; }

.modal-actions-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.action-btn { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; padding: 20px; border-radius: 14px; border: none; cursor: pointer; transition: all 0.2s; font-weight: 800; color: white; }
.btn-checkin { background: #10b981; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }
.btn-checkout { background: #ef4444; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3); }

/* 6. Preview Modal Specifics - สไตล์สำหรับเลเยอร์ดูภาพ */
.modal-overlay.preview { background: rgba(0, 0, 0, 0.7); }
.photo-frame { width: 100%; border-radius: 12px; overflow: hidden; background: #000; margin-bottom: 20px; aspect-ratio: 3/4; display: flex; align-items: center; }
.preview-img { width: 100%; height: 100%; object-fit: cover; }
.photo-info { background: #f8fafc; padding: 12px 16px; border-radius: 10px; display: flex; justify-content: space-between; }

/* การจัดการ Responsive สำหรับมือถือ */
@media (max-width: 480px) {
  .attendance-header { flex-direction: column; align-items: center; gap: 20px; }
  .header-actions { align-items: center; width: 100%; }
  .action-group { width: 100%; justify-content: center; gap: 8px; flex-wrap: wrap; }
  .btn-action-square { width: 22%; max-width: 85px; height: 75px; }
  .time-display-large { font-size: 2rem; }
}
/* --- OT Detail Modal (Premium Design) --- */
.detail-modal {
  max-width: 450px !important;
  border-radius: 24px !important;
  background: #1e2227 !important;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6) !important;
  overflow: hidden;
}

.detail-modal .modal-header {
  background: rgba(255, 255, 255, 0.03) !important;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
}

.detail-modal .modal-header h3 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #fff !important;
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-modal .modal-header h3 i {
  color: #3b82f6;
  font-size: 1.4rem;
}

.detail-modal .modal-body {
  padding: 24px;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item.full {
  grid-column: span 2;
}

.detail-item label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #94a3b8 !important;
  text-transform: uppercase;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-item .val {
  font-size: 1rem;
  color: #f1f5f9 !important;
  font-weight: 500;
}

.val.highlight {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.1));
  padding: 16px;
  border-radius: 16px;
  text-align: center;
  font-size: 1.4rem !important;
  font-weight: 800 !important;
  color: #60a5fa !important;
  border: 1px solid rgba(59, 130, 246, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.text-special {
  color: #fbbf24 !important;
}

.total-row {
  margin-top: 10px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.val.large {
  font-size: 2.2rem !important;
  font-weight: 900 !important;
  color: #10b981 !important;
  letter-spacing: -1px;
}

.reason-box {
  background: rgba(0, 0, 0, 0.2);
  padding: 14px;
  border-radius: 12px;
  border-left: 3px solid #3b82f6;
  font-size: 0.9rem;
  color: #cbd5e1 !important;
  line-height: 1.5;
  font-style: italic;
}

.detail-modal .ot-status-badge {
  padding: 6px 14px;
  font-size: 0.75rem;
  border-radius: 20px;
  font-weight: 700;
}

.detail-modal .ot-status-badge.pending { background: #fffbeb; color: #d97706; }
.detail-modal .ot-status-badge.approved { background: #f0fdf4; color: #16a34a; }
.detail-modal .ot-status-badge.rejected { background: #fef2f2; color: #dc2626; }

@media (max-width: 480px) {
  .detail-modal { width: 95%; margin: 10px; }
  .detail-grid { grid-template-columns: 1fr; }
}

</style>
