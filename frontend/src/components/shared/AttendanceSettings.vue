<template>
  <div class="attendance-settings-container">
    <div class="header-section">
      <div class="header-titles">
        <h2><i class="fas fa-business-time"></i> Time & Leave Settings</h2>
        <p class="subtitle">Configuration panel for attendance, location, and annual leave quotas.</p>
      </div>
      <div class="header-status">
        <span class="status-badge"><i class="fas fa-shield-alt"></i> Admin Control</span>
      </div>
    </div>

    <div class="settings-grid">
      <!-- LEFT COLUMN -->
      <div class="settings-col">
        <!-- 1. WORKING HOURS -->
        <div class="card">
          <div class="card-header">
            <h3><i class="fas fa-clock"></i> Standard Working Hours</h3>
            <button class="btn-primary-sm" @click="saveConfigs('hours')">Save Settings</button>
          </div>
          <div class="card-body">
            <div class="form-row">
              <div class="field">
                <label>Check-in <span class="tag-24h">24H</span></label>
                <input type="text" class="input-modern" v-model="config.check_in_time" placeholder="HH:mm" @blur="validateTime('check_in_time')" />
              </div>
              <div class="field">
                <label>Check-out <span class="tag-24h">24H</span></label>
                <input type="text" class="input-modern" v-model="config.check_out_time" placeholder="HH:mm" @blur="validateTime('check_out_time')" />
              </div>
            </div>
            
            <div class="grace-periods-container">
              <label class="section-label">Grace Periods (Late Tiers)</label>
              <div class="grace-grid">
                <div class="grace-field">
                  <div class="grace-tag t1">Tier 1</div>
                  <div class="grace-input-wrap">
                    <input type="number" v-model="config.late_grace_period_mins" />
                    <span>min</span>
                  </div>
                </div>
                <div class="grace-field">
                  <div class="grace-tag t2">Tier 2</div>
                  <div class="grace-input-wrap">
                    <input type="number" v-model="config.late_grace_period_mins_t2" />
                    <span>min</span>
                  </div>
                </div>
                <div class="grace-field">
                  <div class="grace-tag t3">Tier 3</div>
                  <div class="grace-input-wrap">
                    <input type="number" v-model="config.late_grace_period_mins_t3" />
                    <span>min</span>
                  </div>
                </div>
              </div>
              <p class="help-text">Define allowed lateness levels before penalty status changes.</p>
            </div>
          </div>
        </div>

        <!-- 3. OVERTIME RULES -->
        <div class="card">
          <div class="card-header">
            <h3><i class="fas fa-business-time"></i> Overtime Configuration</h3>
            <button class="btn-primary-sm" @click="saveConfigs('ot')">Update OT</button>
          </div>
          <div class="card-body">
            <div class="ot-list">
              <div class="ot-row">
                <div class="ot-info">
                  <span class="ot-name">Standard Overtime <span class="tag-24h-ot">24H</span></span>
                  <small>Default after-hours rate</small>
                </div>
                <div class="ot-inputs">
                  <input type="text" class="time-text-input" v-model="config.ot_normal_start" placeholder="HH:mm" @blur="validateTime('ot_normal_start')" />
                  <span class="sep">to</span>
                  <input type="text" class="time-text-input" v-model="config.ot_normal_end" placeholder="HH:mm" @blur="validateTime('ot_normal_end')" />
                </div>
              </div>
              <div class="ot-row">
                <div class="ot-info">
                  <span class="ot-name">Special Overtime <span class="tag-24h-ot">24H</span></span>
                  <small>Holiday / Midnight shift</small>
                </div>
                <div class="ot-inputs">
                  <input type="text" class="time-text-input" v-model="config.ot_special_start" placeholder="HH:mm" @blur="validateTime('ot_special_start')" />
                  <span class="sep">to</span>
                  <input type="text" class="time-text-input" v-model="config.ot_special_end" placeholder="HH:mm" @blur="validateTime('ot_special_end')" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 4. LEAVE QUOTAS -->
        <div class="card">
          <div class="card-header">
            <h3><i class="fas fa-calendar-alt"></i> Annual Leave Quotas</h3>
            <button class="btn-primary-sm" @click="saveConfigs('leaves')">Save Quotas</button>
          </div>
          <div class="card-body quota-body">
            <div class="quota-item">
              <div class="q-icon"><i class="fas fa-briefcase-medical"></i></div>
              <div class="q-data">
                <label>Sick Leave</label>
                <div class="q-val-wrap">
                   <input type="number" v-model="config.quota_sick_leave" />
                   <span>days</span>
                </div>
              </div>
            </div>
            <div class="quota-item">
              <div class="q-icon"><i class="fas fa-umbrella-beach"></i></div>
              <div class="q-data">
                <label>Annual Leave</label>
                <div class="q-val-wrap">
                   <input type="number" v-model="config.quota_annual_leave" />
                   <span>days</span>
                </div>
              </div>
            </div>
            <div class="quota-item">
              <div class="q-icon"><i class="fas fa-user-clock"></i></div>
              <div class="q-data">
                <label>Personal Leave</label>
                <div class="q-val-wrap">
                   <input type="number" v-model="config.quota_personal_leave" />
                   <span>days</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT COLUMN -->
      <div class="settings-col">
        <!-- 2. LOCATION MANAGEMENT -->
        <div class="card loc-card">
          <div class="card-header">
            <h3><i class="fas fa-map-marked-alt"></i> Location Management</h3>
            <div class="segment-ctrl">
              <button :class="{ active: activeLocTab === 'fixed' }" @click="activeLocTab = 'fixed'">Fixed</button>
              <button :class="{ active: activeLocTab === 'onsite' }" @click="activeLocTab = 'onsite'">On-site</button>
            </div>
          </div>
          <div class="card-action-bar">
            <span>{{ filteredLocations.length }} Selected Sites</span>
            <button @click="showAddLocModal = true"><i class="fas fa-plus"></i> New Location</button>
          </div>
          <div class="card-body p-0 list-scroll">
            <div v-for="loc in filteredLocations" :key="loc.id" class="list-item">
              <div class="item-icon" :class="{ fixed: loc.is_fixed }">
                 <i :class="loc.is_fixed ? 'fas fa-building' : 'fas fa-hard-hat'"></i>
              </div>
              <div class="item-content">
                <div class="item-primary">{{ loc.name }}</div>
                <div class="item-secondary">
                  <span>Radius: {{ loc.radius }}m</span>
                  <span class="dot">•</span>
                  <span>{{ loc.lat.toFixed(6) }}, {{ loc.lon.toFixed(6) }}</span>
                </div>
              </div>
              <button class="item-del" @click="deleteLocation(loc.id)"><i class="fas fa-trash-alt"></i></button>
            </div>
            <div v-if="filteredLocations.length === 0" class="empty-hint">
              <i class="fas fa-map-marker-alt"></i>
              <p>No locations registered</p>
            </div>
          </div>
        </div>

        <!-- 5. PUBLIC HOLIDAYS -->
        <div class="card hol-card">
          <div class="card-header">
            <div class="header-flex">
              <h3><i class="fas fa-calendar-check"></i> Holidays</h3>
              <select v-model="selectedYear" class="select-clean">
                <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
              </select>
            </div>
            <button class="btn-ghost-sm" @click="addHoliday">+ Add</button>
          </div>
          <div class="card-body p-0 list-scroll-sm">
            <div v-for="hol in holidays" :key="hol.id" class="hol-row">
              <div class="hol-date">
                <span class="d">{{ new Date(hol.date).getDate() }}</span>
                <span class="m">{{ new Date(hol.date).toLocaleString('default', { month: 'short' }) }}</span>
              </div>
              <div class="hol-input">
                <input type="text" v-model="hol.name" placeholder="Holiday Title" />
              </div>
              <button @click="deleteHoliday(hol)"><i class="fas fa-times"></i></button>
            </div>
            <div v-if="holidays.length === 0" class="empty-hint-sm">No holidays for this year.</div>
          </div>
        </div>
      </div>
    </div>

    <!-- MAP MODAL (THEMED) -->
    <div v-if="showAddLocModal" class="modal-overlay" @click.self="showAddLocModal = false">
      <div class="modal-container">
        <div class="modal-header">
          <div class="m-titles">
             <h3>Configure Location</h3>
             <p>Pinpoint the operational site coordinates</p>
          </div>
          <button @click="showAddLocModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="modal-sidebar">
            <div class="m-field">
              <label>Location Name</label>
              <input v-model="newLoc.name" placeholder="HQ, Factory A, etc." />
            </div>
            <div class="m-row">
              <div class="m-field">
                <label>Latitude</label>
                <input :value="newLoc.lat.toFixed(6)" readonly class="dim" />
              </div>
              <div class="m-field">
                <label>Longitude</label>
                <input :value="newLoc.lon.toFixed(6)" readonly class="dim" />
              </div>
            </div>
            <div class="m-field">
              <label>Interaction Radius (m)</label>
              <input v-model.number="newLoc.radius" type="number" />
            </div>
            
            <button class="btn-sec" @click="locateMe"><i class="fas fa-location-arrow"></i> Find My GPS</button>
            <button class="btn-pri" @click="saveNewLocation" :disabled="!newLoc.name">Save New Location</button>
          </div>
          <div class="modal-map">
            <div id="map-container" ref="mapContainer"></div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import api from '../../api'
import Swal from 'sweetalert2'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Leaflet Icon Fix
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'
let defaultIcon = L.icon({ iconUrl: markerIcon, shadowUrl: markerShadow, iconSize: [25, 41], iconAnchor: [12, 41] })

const config = ref({
  check_in_time: '08:00', check_out_time: '17:00', 
  late_grace_period_mins: '5', 
  late_grace_period_mins_t2: '15', 
  late_grace_period_mins_t3: '30',
  ot_normal_start: '17:00', ot_normal_end: '22:00', ot_special_start: '22:00', ot_special_end: '06:00',
  quota_sick_leave: '30', quota_annual_leave: '6', quota_personal_leave: '3'
})

const activeLocTab = ref('fixed')
const locations = ref([])
const holidays = ref([])
const selectedYear = ref(new Date().getFullYear())
const showAddLocModal = ref(false)
const mapContainer = ref(null)
let map = null, marker = null, circle = null
const newLoc = ref({ name: '', lat: 13.7563, lon: 100.5018, radius: 100 })

const filteredLocations = computed(() => locations.value.filter(l => activeLocTab.value === 'fixed' ? l.is_fixed : !l.is_fixed))

const initMap = () => {
  if (map) return
  map = L.map('map-container').setView([newLoc.value.lat, newLoc.value.lon], 16)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map)
  marker = L.marker([newLoc.value.lat, newLoc.value.lon], { icon: defaultIcon, draggable: true }).addTo(map)
  circle = L.circle([newLoc.value.lat, newLoc.value.lon], { radius: newLoc.value.radius, color: '#1a2a3a', fillOpacity: 0.15 }).addTo(map)
  marker.on('dragend', (e) => updateMarkerPos(e.target.getLatLng().lat, e.target.getLatLng().lng))
  map.on('click', (e) => updateMarkerPos(e.latlng.lat, e.latlng.lng))
}

const updateMarkerPos = (lat, lon) => {
  newLoc.value.lat = lat; newLoc.value.lon = lon
  if (marker) marker.setLatLng([lat, lon])
  if (circle) circle.setLatLng([lat, lon])
}

const locateMe = () => {
  if (!navigator.geolocation) return Swal.fire('Error', 'GPS not supported', 'error')
  Swal.fire({ title: 'Locating...', allowOutsideClick: false, didOpen: () => Swal.showLoading() })
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      updateMarkerPos(pos.coords.latitude, pos.coords.longitude)
      if (map) map.setView([pos.coords.latitude, pos.coords.longitude], 18)
      Swal.close()
    },
    () => { Swal.close(); Swal.fire('Error', 'GPS Restricted', 'error') },
    { enableHighAccuracy: true }
  )
}

watch(() => newLoc.value.radius, (v) => circle && circle.setRadius(v || 100))
watch(showAddLocModal, async (v) => {
  if (v) {
    newLoc.value = { name: '', lat: 13.7563, lon: 100.5018, radius: 100 }
    await nextTick(); setTimeout(() => { if (mapContainer.value) { initMap(); map.invalidateSize(); } }, 200)
  } else if (map) { map.remove(); map = null; }
})

const fetchConfigs = async () => {
  try {
    const res = await api.get('/attendance/settings')
    res.data.forEach(item => { if (config.value[item.key] !== undefined) config.value[item.key] = item.value })
  } catch (err) { console.error(err) }
}

// ฟังก์ชันช่วยเช็คและบังคับรูปแบบ 24 ชั่วโมงตอนกรอก
const validateTime = (key) => {
  const val = config.value[key]
  if (!val) return
  
  // ล้างตัวอักษรขยะและเว้นวรรค
  let clean = val.trim().replace(/[^0-9:]/g, '')
  
  // ถ้าพิมเลข 4 ตัวติดกัน (เช่น 1530) ให้เติม : ให้อัตโนมัติเป็น 15:30
  if (clean.length === 4 && !clean.includes(':')) {
    clean = clean.slice(0, 2) + ':' + clean.slice(2)
  }
  
  // ตรวจสอบความถูกต้องของ HH:mm แบบ 24 ชั่วโมง
  const regex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/
  if (!regex.test(clean)) {
    Swal.fire({
      icon: 'error',
      title: 'รูปแบบเวลาไม่ถูกต้อง',
      text: 'กรุณากรอกเป็นรูปแบบ 24 ชม. (เช่น 08:30 หรือ 17:00)',
      confirmButtonColor: '#1a2a3a'
    })
    config.value[key] = "00:00"
  } else {
    // เติมเลข 0 ด้านหน้าถ้ากรอกแบบเลขเดี่ยว (เช่น 8:30 -> 08:30)
    const [h, m] = clean.split(':')
    config.value[key] = `${h.padStart(2, '0')}:${m.padStart(2, '0')}`
  }
}
const fetchLocations = async () => {
  try { const res = await api.get('/attendance/locations'); locations.value = res.data } catch (err) { console.error(err) }
}
const saveNewLocation = async () => {
  try {
    await api.post('/attendance/locations', { ...newLoc.value, is_fixed: activeLocTab.value === 'fixed' })
    Swal.fire({ icon: 'success', title: 'Saved', toast: true, position: 'top-end', showConfirmButton: false, timer: 1500 })
    showAddLocModal.value = false; fetchLocations()
  } catch (err) { console.error(err) }
}
const deleteLocation = async (id) => {
  const res = await Swal.fire({ title: 'Delete?', icon: 'warning', showCancelButton: true, confirmButtonColor: '#1a2a3a' })
  if (res.isConfirmed) { try { await api.delete(`/attendance/locations/${id}`); fetchLocations() } catch (err) { console.error(err) } }
}
const saveConfigs = async (type) => {
  try {
    let keys = []
    if (type === 'hours') keys = ['check_in_time', 'check_out_time', 'late_grace_period_mins', 'late_grace_period_mins_t2', 'late_grace_period_mins_t3']
    if (type === 'ot') keys = ['ot_normal_start', 'ot_normal_end', 'ot_special_start', 'ot_special_end']
    if (type === 'leaves') keys = ['quota_sick_leave', 'quota_annual_leave', 'quota_personal_leave']
    const payload = keys.map(k => ({ key: k, value: String(config.value[k]) }))
    await api.put('/attendance/settings', payload)
    Swal.fire({ icon: 'success', title: 'Updated', toast: true, position: 'top-end', showConfirmButton: false, timer: 2000 })
  } catch (err) { console.error(err) }
}
const fetchHolidays = async () => {
  try { const res = await api.get(`/attendance/holidays/${selectedYear.value}`); holidays.value = res.data || [] } catch (err) { console.error(err) }
}

watch(selectedYear, () => {
  fetchHolidays()
})

const availableYears = computed(() => {
  const y = new Date().getFullYear()
  return [y - 1, y, y + 1]
})
const addHoliday = async () => {
  const { value: v } = await Swal.fire({
    title: 'Add Holiday',
    html: `<input id="h-date" type="date" class="swal2-input"><input id="h-name" class="swal2-input" placeholder="Title">`,
    showCancelButton: true, preConfirm: () => ({ date: document.getElementById('h-date').value, name: document.getElementById('h-name').value })
  })
  if (v?.date) { await api.post('/attendance/holidays', { year: selectedYear.value, ...v }); fetchHolidays() }
}
const deleteHoliday = async (hol) => {
  try { await api.delete(`/attendance/holidays/${hol.id}`); fetchHolidays() } catch (err) { console.error(err) }
}

onMounted(() => { fetchConfigs(); fetchLocations(); fetchHolidays() })
</script>

<style scoped>
/* ────────── THEME CONSISTENCY ────────── */
.attendance-settings-container {
  display: flex; flex-direction: column; gap: 24px; padding: 10px;
  font-family: 'Inter', -apple-system, sans-serif;
  color: #334155;
}

/* ────────── HEADER ────────── */
.header-section {
  display: flex; justify-content: space-between; align-items: flex-start;
  padding-bottom: 20px; border-bottom: 1px solid #e2e8f0;
}
.header-titles h2 { margin: 0; font-size: 1.5rem; font-weight: 800; color: #1a2a3a; display: flex; align-items: center; gap: 12px; }
.subtitle { margin: 4px 0 0; font-size: 0.9rem; color: #64748b; }
.status-badge { background: #f1f5f9; padding: 6px 14px; border-radius: 100px; font-size: 0.75rem; font-weight: 700; color: #1a2a3a; border: 1px solid #e2e8f0; }

.tag-24h { font-size: 0.6rem; background: #1a2a3a; color: #fff; padding: 1px 4px; border-radius: 3px; margin-left: 4px; vertical-align: middle; }
.tag-24h-ot { font-size: 0.55rem; border: 1px solid #cbd5e1; color: #64748b; padding: 1px 3px; border-radius: 3px; margin-left: 6px; }

/* ────────── GRID ────────── */
.settings-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
@media (max-width: 1024px) { .settings-grid { grid-template-columns: 1fr; } }

/* ────────── CARD BASE ────────── */
.card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden; }
.card-header { padding: 16px 20px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; background: #fafafa; }
.card-header h3 { margin: 0; font-size: 0.95rem; font-weight: 700; color: #1a2a3a; display: flex; align-items: center; gap: 8px; }
.card-body { padding: 20px; }
.card-body.p-0 { padding: 0; }

/* ────────── FORMS ────────── */
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field.full { grid-column: span 2; }
.field label { font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; }
.input-modern { padding: 10px 12px; border: 1.5px solid #e2e8f0; border-radius: 8px; font-size: 0.9rem; transition: 0.2s; }
.input-modern:focus { border-color: #1a2a3a; outline: none; }

.btn-primary-sm { background: #1a2a3a; color: #fff; border: none; padding: 6px 14px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; cursor: pointer; }
.btn-primary-sm:hover { background: #243447; }

/* ────────── GRACE PERIODS (LATE TIERS) ────────── */
.grace-periods-container {
  padding-top: 16px; border-top: 1px dashed #e2e8f0;
}
.section-label { display: block; font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 12px; }
.grace-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.grace-field { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px; display: flex; flex-direction: column; gap: 8px; }
.grace-tag { font-size: 0.65rem; font-weight: 800; padding: 2px 6px; border-radius: 4px; align-self: flex-start; text-transform: uppercase; }
.grace-tag.t1 { background: #fef9c3; color: #854d0e; } /* Yellow */
.grace-tag.t2 { background: #ffedd5; color: #9a3412; } /* Orange */
.grace-tag.t3 { background: #fee2e2; color: #991b1b; } /* Red */

.grace-input-wrap { display: flex; align-items: center; gap: 4px; }
.grace-input-wrap input { width: 100%; border: none; background: transparent; font-size: 1.1rem; font-weight: 800; color: #1a2a3a; outline: none; }
.grace-input-wrap span { font-size: 0.65rem; font-weight: 600; color: #94a3b8; }
.help-text { font-size: 0.7rem; color: #94a3b8; margin-top: 10px; font-style: italic; }

/* ────────── OT LIST ────────── */
.ot-list { display: flex; flex-direction: column; gap: 16px; }
.ot-row { 
  display: grid; 
  grid-template-columns: 1fr 240px; 
  align-items: center; 
  padding: 16px 20px; 
  background: #f8fafc; 
  border-radius: 12px; 
  border: 1px solid #e2e8f0;
  transition: 0.2s;
}
.ot-row:hover { border-color: #1a2a3a; background: #fff; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }

.ot-info { display: flex; flex-direction: column; gap: 2px; }
.ot-name { font-size: 0.82rem; font-weight: 800; color: #1a2a3a; text-transform: uppercase; letter-spacing: 0.01em; }
.ot-info small { font-size: 0.72rem; color: #94a3b8; font-weight: 500; }

.ot-inputs { display: flex; align-items: center; justify-content: flex-end; gap: 6px; }
.ot-inputs input { 
  width: 70px; 
  padding: 8px 4px; 
  border: 1.5px solid #cbd5e1; 
  border-radius: 6px; 
  font-size: 0.9rem; 
  font-weight: 700; 
  text-align: center;
  color: #1a2a3a;
  background: #fff;
}
.ot-inputs input:focus { border-color: #1a2a3a; outline: none; box-shadow: 0 0 0 3px rgba(26,42,58,0.1); }
.sep { color: #94a3b8; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; }

/* ────────── QUOTAS ────────── */
.quota-body { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.quota-item { padding: 16px 10px; background: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0; text-align: center; }
.q-icon { font-size: 1.1rem; color: #1a2a3a; margin-bottom: 8px; opacity: 0.7; }
.q-data label { display: block; font-size: 0.7rem; font-weight: 700; color: #64748b; margin-bottom: 4px; }
.q-val-wrap { display: flex; align-items: baseline; justify-content: center; gap: 4px; }
.q-val-wrap input { width: 45px; background: transparent; border: none; font-size: 1.2rem; font-weight: 800; color: #1a2a3a; text-align: right; outline: none; }
.q-val-wrap span { font-size: 0.65rem; font-weight: 600; color: #94a3b8; }

/* ────────── LOCATION CARD ────────── */
.segment-ctrl { display: flex; background: #f1f5f9; padding: 3px; border-radius: 8px; }
.segment-ctrl button { border: none; background: none; padding: 4px 12px; font-size: 0.75rem; font-weight: 700; border-radius: 6px; cursor: pointer; color: #64748b; }
.segment-ctrl button.active { background: #fff; color: #1a2a3a; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }

.card-action-bar { padding: 10px 20px; background: #fafafa; border-bottom: 1px dashed #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.card-action-bar span { font-size: 0.75rem; font-weight: 700; color: #1a2a3a; }
.card-action-bar button { background: #1a2a3a; color: #fff; border: none; padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; cursor: pointer; display: flex; align-items: center; gap: 4px; }

.list-scroll { max-height: 380px; overflow-y: auto; }
.list-item { display: flex; align-items: center; gap: 12px; padding: 12px 20px; border-bottom: 1px solid #f1f5f9; }
.item-icon { width: 36px; height: 36px; border-radius: 8px; background: #f1f5f9; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; color: #64748b; }
.item-icon.fixed { background: #e0f2fe; color: #0369a1; }
.item-primary { font-size: 0.85rem; font-weight: 700; color: #1a2a3a; }
.item-secondary { font-size: 0.7rem; color: #94a3b8; font-family: monospace; margin-top: 2px; }
.dot { margin: 0 4px; }
.item-del { margin-left: auto; background: none; border: none; color: #cbd5e1; cursor: pointer; transition: 0.2s; }
.item-del:hover { color: #ef4444; }

/* ────────── HOLIDAYS ────────── */
.header-flex { display: flex; align-items: center; gap: 8px; }
.select-clean { background: #f1f5f9; border: none; font-size: 0.85rem; font-weight: 800; border-radius: 6px; padding: 4px 8px; cursor: pointer; color: #1a2a3a; }
.btn-ghost-sm { border: 1px solid #e2e8f0; background: #fff; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 6px; cursor: pointer; transition: 0.2s; color: #64748b; }
.btn-ghost-sm:hover { border-color: #1a2a3a; color: #1a2a3a; }

.list-scroll-sm { max-height: 250px; overflow-y: auto; }
.hol-row { 
  display: flex; 
  align-items: center; 
  gap: 16px; 
  padding: 14px 20px; 
  border-bottom: 1px solid #f1f5f9; 
  transition: 0.2s;
}
.hol-row:hover { background: #fcfcfc; }
.hol-date { 
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  border-right: 2px solid #e2e8f0; 
  padding-right: 16px; 
  width: 55px; 
  flex-shrink: 0;
}
.hol-date .d { font-weight: 800; font-size: 1.1rem; color: #1a2a3a; line-height: 1; }
.hol-date .m { font-size: 0.65rem; text-transform: uppercase; color: #94a3b8; font-weight: 700; }
.hol-input { flex: 1; margin-left: 4px; }
.hol-input input { 
  border: none; 
  background: transparent; 
  font-size: 0.95rem; 
  font-weight: 600; 
  color: #334155; 
  width: 100%; 
  outline: none; 
  padding: 4px 0;
}
.hol-input input:focus { color: #1a2a3a; }
.hol-row button { 
  background: none; 
  border: none; 
  color: #cbd5e1; 
  font-size: 0.9rem; 
  padding: 8px; 
  cursor: pointer; 
  transition: 0.2s;
  margin-left: auto;
}
.hol-row button:hover { color: #ef4444; transform: scale(1.1); }

/* ────────── MODAL (THEMED) ────────── */
.modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.6); display: flex; align-items: center; justify-content: center; z-index: 999; padding: 20px; }
.modal-container { background: #fff; width: 100%; max-width: 900px; border-radius: 12px; display: flex; flex-direction: column; height: 80vh; overflow: hidden; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
.modal-header { padding: 16px 24px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.m-titles h3 { margin: 0; font-size: 1.1rem; font-weight: 800; color: #1a2a3a; }
.m-titles p { margin: 2px 0 0; font-size: 0.8rem; color: #64748b; }
.modal-header button { background: none; border: none; font-size: 1.2rem; cursor: pointer; color: #94a3b8; }

.modal-body { display: flex; flex: 1; overflow: hidden; }
.modal-sidebar { width: 300px; border-right: 1px solid #e2e8f0; padding: 24px; display: flex; flex-direction: column; gap: 16px; background: #fafafa; }
.modal-map { flex: 1; background: #eee; position: relative; }
#map-container { position: absolute; inset: 0; }

.m-field { display: flex; flex-direction: column; gap: 4px; }
.m-field label { font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase; }
.m-field input { padding: 8px 12px; border: 1.5px solid #e2e8f0; border-radius: 6px; font-size: 0.9rem; }
.m-field input.dim { background: #f1f5f9; color: #94a3b8; font-family: monospace; }
.m-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

.btn-pri { background: #1a2a3a; color: #fff; border: none; padding: 12px; border-radius: 8px; font-weight: 700; cursor: pointer; margin-top: auto; }
.btn-pri:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-sec { background: transparent; border: 1.5px solid #1a2a3a; color: #1a2a3a; padding: 10px; border-radius: 8px; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; }

.empty-hint { text-align: center; padding: 40px; color: #cbd5e1; }
.empty-hint i { font-size: 2rem; margin-bottom: 10px; }

@media (max-width: 768px) {
  .modal-body { flex-direction: column; }
  .modal-sidebar { width: 100%; height: auto; border-right: none; border-bottom: 1px solid #e2e8f0; }
}
</style>
