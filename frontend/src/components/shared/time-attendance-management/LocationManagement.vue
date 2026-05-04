<template>
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
import api from '../../../api'
import Swal from 'sweetalert2'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Leaflet Icon Fix
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'
let defaultIcon = L.icon({ iconUrl: markerIcon, shadowUrl: markerShadow, iconSize: [25, 41], iconAnchor: [12, 41] })

const activeLocTab = ref('fixed')
const locations = ref([])
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
    await nextTick(); setTimeout(() => { initMap(); map?.invalidateSize(); }, 200)
  } else if (map) { map.remove(); map = null; }
})

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

onMounted(() => { fetchLocations() })
</script>

<style scoped>
.loc-card { height: 100%; display: flex; flex-direction: column; }
.segment-ctrl { display: flex; background: #f1f5f9; padding: 3px; border-radius: 8px; }
.segment-ctrl button { border: none; background: none; padding: 4px 12px; font-size: 0.75rem; font-weight: 700; border-radius: 6px; cursor: pointer; color: #64748b; }
.segment-ctrl button.active { background: #fff; color: #1a2a3a; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }

.card-action-bar { padding: 10px 20px; background: #fafafa; border-bottom: 1px dashed #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.card-action-bar span { font-size: 0.75rem; font-weight: 700; color: #1a2a3a; }
.card-action-bar button { background: #1a2a3a; color: #fff; border: none; padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; cursor: pointer; display: flex; align-items: center; gap: 4px; }

.list-scroll { max-height: 400px; overflow-y: auto; flex: 1; }
.list-item { display: flex; align-items: center; gap: 12px; padding: 12px 20px; border-bottom: 1px solid #f1f5f9; }
.item-icon { width: 36px; height: 36px; border-radius: 8px; background: #f1f5f9; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; color: #64748b; }
.item-icon.fixed { background: #e0f2fe; color: #0369a1; }
.item-primary { font-size: 0.85rem; font-weight: 700; color: #1a2a3a; }
.item-secondary { font-size: 0.7rem; color: #94a3b8; font-family: monospace; margin-top: 2px; }
.item-del { margin-left: auto; background: none; border: none; color: #cbd5e1; cursor: pointer; transition: 0.2s; }
.item-del:hover { color: #ef4444; }
.empty-hint { padding: 60px 20px; text-align: center; color: #94a3b8; }
.empty-hint i { font-size: 2rem; margin-bottom: 10px; opacity: 0.3; }

/* MODAL */
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
.m-field input { padding: 10px; border: 1.5px solid #e2e8f0; border-radius: 8px; outline: none; }
.m-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.dim { background: #f1f5f9; color: #64748b; }
.btn-pri { background: #1a2a3a; color: #fff; border: none; padding: 12px; border-radius: 8px; font-weight: 700; cursor: pointer; margin-top: auto; }
.btn-sec { background: #fff; border: 1.5px solid #e2e8f0; padding: 10px; border-radius: 8px; font-size: 0.85rem; font-weight: 700; cursor: pointer; color: #475569; }
</style>
