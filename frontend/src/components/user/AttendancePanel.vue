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
          <!-- ปุ่ม On-Site (ใช้ลงเวลานอกสถานที่) -->
          <button class="btn-action-square btn-onsite" @click="handleOnSiteCheckin">
            <i class="fas fa-map-marker-alt"></i>
            <span>ON-SITE</span>
          </button>
          
          <!-- ปุ่ม By User (ลงเวลาผ่านแอปมือถือ/ถ่ายรูป) -->
          <button class="btn-action-square btn-user" @click="handleCheckinUser">
            <i class="fas fa-user-clock"></i>
            <span>BY USER</span>
          </button>
          
          <!-- ปุ่ม Factory (ลงเวลาในโรงงาน) -->
          <button class="btn-action-square btn-factory" @click="handleCheckinFactory">
            <i class="fas fa-industry"></i>
            <span>FACTORY</span>
          </button>
          
          <!-- ปุ่มขอ OT -->
          <button class="btn-action-square btn-ot" @click="handleOTRequest">
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
              <!-- แสดงเวลาเข้างาน และสถานะสาย (มาพร้อมตัวบ่งชี้สี) -->
              <td class="col-time">
                <div v-if="day.clockIn !== '—'" class="time-status-wrap">
                  <!-- คลิกที่เวลาเพื่อดูรูปถ่ายตอนเช็คอิน -->
                  <span @click="showPhotoPreview(day.inImage, day.inFullTime, 'Clock IN')" 
                        class="clickable-time"
                        :style="{ color: getStatusColor(day.status) }">
                    {{ day.clockIn }}
                  </span>
                  <!-- ป้ายสถานะ (แสดงจำนวนนาทีที่สาย) -->
                  <span class="status-mini-label" :style="{ backgroundColor: getStatusBg(day.status), color: getStatusColor(day.status) }">
                    {{ formatStatusLabel(day.status, day.lateMinutes) }}
                  </span>
                </div>
                <span v-else class="empty-val">—</span>
              </td>
              <!-- แสดงเวลาออกงาน -->
              <td class="col-time">
                <span v-if="day.clockOut !== '—'" @click="showPhotoPreview(day.outImage, day.outFullTime, 'Clock OUT')" class="clickable-time">
                  {{ day.clockOut }}
                </span>
                <span v-else class="empty-val">—</span>
              </td>
              <!-- แสดงจำนวน OT ( hrs.) -->
              <td class="col-ot">{{ day.ot }}</td>
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


    <!-- [6] หน้าต่าง Modal สำหรับพนักงานกดลงเวลาเอง (BY USER) -->
    <div v-if="isUserCheckinModalOpen" class="modal-overlay" @click="isUserCheckinModalOpen = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3><i class="fas fa-user-clock"></i> User Check-in / Out</h3>
          <button class="close-btn" @click="isUserCheckinModalOpen = false"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body">
          <div class="checkin-form">
            <label class="form-label">สถานที่ลงเวลา (Location)</label>
            <!-- เลือกโหมด: ทำงานที่โรงงาน หรือ ออกไซด์งานข้างนอก -->
            <div class="location-tabs">
              <button :class="['loc-tab', { active: checkInType === 'factory' }]" @click="checkInType = 'factory'">Factory</button>
              <button :class="['loc-tab', { active: checkInType === 'site' }]" @click="checkInType = 'site'">On-Site</button>
            </div>
            
            <p v-if="geoError" class="geo-error">{{ geoError }}</p>
          </div>

          <!-- ปุ่มกดยืนยัน เข้างาน / ออกงาน (ระบบจะเรียกกล้องมือถือให้อัตโนมัติ) -->
          <div class="modal-actions-row">
            <button class="action-btn btn-checkin" @click="triggerCamera('in')" :disabled="isUploading">
              <i class="fas fa-sign-in-alt"></i>
              <span>{{ isUploading && currentAction === 'in' ? 'Processing...' : 'Clock IN' }}</span>
            </button>
            <button class="action-btn btn-checkout" @click="triggerCamera('out')" :disabled="isUploading">
              <i class="fas fa-sign-out-alt"></i>
              <span>{{ isUploading && currentAction === 'out' ? 'Processing...' : 'Clock OUT' }}</span>
            </button>
          </div>

          <!-- Input ลับสำหรับเปิดกล้องถ่ายภาพ (Hidden) -->
          <input type="file" ref="cameraInput" accept="image/*" capture="user" style="display: none;" @change="handlePhotoTaken" />
        </div>
      </div>
    </div>

    <!-- [7] หน้าต่าง Modal สำหรับขอโอที (OT Request) -->
    <OTRequestModal 
      :isOpen="isOTModalOpen" 
      :requesterName="requesterName" 
      :attendanceLogs="historyLogs"
      @close="isOTModalOpen = false"
      @submitted="fetchMyAttendance"
    />

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import api from '../../api'
import OTRequestModal from './OTRequestModal.vue'

const props = defineProps(['userId'])

// --- 1. ตัวแปรสถานะระบบ (Core State) ---
const currentTime = ref('00:00:00') // เวลาปัจจุบัน 24H
const currentDate = ref('')        // วันที่ปัจจุบัน
const salaryType = ref('')         // ประเภทเงินเดิอนพนักงาน
const hireDateStr = ref('')        // วันที่เริ่มงาน (ใช้ล็อคปฏิทินย้อนหลัง)
const isLoading = ref(true)        // สถานะโหลดข้อมูล
const baseDate = ref(new Date())   // วันที่ฐานสำหรับแสดงผลในตาราง
const weekDays = ref([])           // อาร์เรย์เก็บข้อมูล 7 วันที่จะโชว์ในตาราง
const historyLogs = ref([])        // ประวัติการเข้างานที่ดึงมาจาก API
const requesterName = ref('User')  // ชื่อผู้ขอ (สำหรับส่งไปใน Modal)

// --- 2. ตัวแปรสถานะเช็คอิน (Registration State) ---
const isUserCheckinModalOpen = ref(false)
const isOTModalOpen = ref(false)   // สถานะเปิด/ปิดหน้าต่างขอ OT
const checkInType = ref('factory')
const cameraInput = ref(null)
const currentAction = ref(null) 
const isUploading = ref(false)
const currentLat = ref(null)
const currentLon = ref(null)
const geoError = ref('')

// --- 3. ตัวแปรสถานะ Modal Preview รูปภาพ ---
const isPreviewModalOpen = ref(false)
const previewImage = ref('')
const previewTimestamp = ref('')
const previewTitle = ref('')

// --- 4. ตัวแปรคงที่ (Constants) ---
const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
const selectedMonth = ref(new Date().getMonth())
const selectedYear = ref(new Date().getFullYear())
const configs = ref({}) // เก็บค่าการตั้งค่าบริษัท (เวลาเข้างาน, Grace Period)
let timerInterval = null

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

// --- 6. ฟังก์ชันช่วยจัดการรูปแบบ (Helper Methods) ---

// --- 6. ฟังก์ชันช่วยจัดการรูปแบบ (Helper Methods) ---

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

// แปลงรหัสสถานะเป็นชื่อแสดงผล
const formatStatusLabel = (status, lateMins = 0) => {
  if (status === 'late_t1' || status === 'late_t2' || status === 'late_t3') {
    return `Late ${lateMins} min`
  }
  if (status === 'none') return ''
  return 'On-Time'
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
    const logDate = day.toISOString().split('T')[0]
    const log = historyLogs.value.find(l => l.date === logDate) // จับคู่ข้อมูลจริงจาก DB
    
    days.push({
      dateStr: day.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
      dayName: day.toLocaleDateString('en-US', { weekday: 'short' }),
      fullDate: logDate,
      clockIn: log?.check_in_time ? formatTime(log.check_in_time) : '—',
      clockOut: log?.check_out_time ? formatTime(log.check_out_time) : '—',
      status: log?.status || 'none',
      lateMinutes: log?.late_minutes || 0, // เพิ่มข้อมูลนาทีที่สาย
      inImage: log?.check_in_image,
      outImage: log?.check_out_image,
      inFullTime: log?.check_in_time ? formatFullTime(log.check_in_time) : '',
      outFullTime: log?.check_out_time ? formatFullTime(log.check_out_time) : '',
      ot: log ? "0.0" : "0.0",
      location: log ? log.site_name : '—'
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
    
    // เก็บชื่อเพื่อแสดงใน Modal
    requesterName.value = `${u.first_name} ${u.last_name}`

    if (u.employee_profile) {
      salaryType.value = u.employee_profile.salary_type || 'monthly'
      hireDateStr.value = u.employee_profile.hire_date || ''
    }
  } catch (e) { console.error(e) }
}


// ดึงประวัติการมาทำงานจริงจาก Database
const fetchMyAttendance = async () => {
  try {
    const endpoint = props.userId ? `/attendance/user/${props.userId}` : '/attendance/me'
    const res = await api.get(endpoint)
    historyLogs.value = res.data || []
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

// แสดงรูปถ่ายขยายใหญ่ใน Modal
const showPhotoPreview = (img, ts, title) => {
  if (!img) {
    previewImage.value = ''
    previewTimestamp.value = ts
    previewTitle.value = title
    isPreviewModalOpen.value = true
    return
  }
  
  // แปลง Path รูปจาก DB เป็น URL ที่เข้าถึงได้จริง
  if (img.startsWith('http')) {
    previewImage.value = img
  } else {
    const currentOrigin = window.location.origin.replace(':5173', ':8000')
    let cleanPath = img.replace(/^uploads\//, '').replace(/^\//, '')
    previewImage.value = `${currentOrigin}/uploads/${cleanPath}`
  }
  previewTimestamp.value = ts
  previewTitle.value = title
  isPreviewModalOpen.value = true
}

// --- 9. กระบวนการเช็คอินและจัดการกล้อง (Check-in / Camera Flow) ---
// เมื่อพนักงานกดปุ่มเริ่มเช็คอิน
const handleCheckinUser = () => {
  isUserCheckinModalOpen.value = true
  if (navigator.geolocation) {
    // ดึงพิกัด GPS ทันทีที่เปิดหน้าต่าง
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        currentLat.value = pos.coords.latitude
        currentLon.value = pos.coords.longitude
      },
      (err) => geoError.value = "GPS Error: Please enable location services"
    )
  }
}

// สั่งเปิดกล้อง (โดยการไปกดปุ่ม <input file> ที่ซ่อนไว้)
const triggerCamera = (action) => {
  currentAction.value = action
  if (cameraInput.value) cameraInput.value.click()
}

// เมื่อถ่ายรูปเสร็จแล้ว (เริ่มกระบวนการอัปโหลดและลงบันทึกใน DB)
const handlePhotoTaken = async (event) => {
  const file = event.target.files[0]
  if (!file) {
    currentAction.value = null
    return
  }

  isUploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    // 1. อัปโหลดรูปภาพก่อน
    const uploadRes = await api.post('/attendance/upload-image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    const imagePath = uploadRes.data.path

    // 2. ส่งข้อมูลบันทึกเวลาพร้อมลิงก์รูปภาพและพิกัด GPS
    if (currentAction.value === 'in') {
      await api.post('/attendance/check-in', {
        check_in_type: checkInType.value,
        location_lat: currentLat.value,
        location_lon: currentLon.value,
        check_in_image: imagePath
      })
      alert("✅ Clock IN Successful")
    } else {
      await api.put('/attendance/check-out', {
        check_out_image: imagePath
      })
      alert("✅ Clock OUT Successful")
    }

    isUserCheckinModalOpen.value = false
    await fetchMyAttendance() // รีเฟรชตารางหลังลงเวลาเสร็จ
  } catch (error) {
    console.error(error)
    alert(error.response?.data?.detail || "Upload Error")
  } finally {
    isUploading.value = false
    currentAction.value = null
    if (cameraInput.value) cameraInput.value.value = ""
  }
}

// ฟังก์ชันรอการพัฒนาเพิ่มเติม
const handleOnSiteCheckin = () => alert("Featured in BY USER section.")
const handleCheckinFactory = () => alert("Featured in BY USER section.")
const handleOTRequest = () => {
  isOTModalOpen.value = true
}

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
</style>
