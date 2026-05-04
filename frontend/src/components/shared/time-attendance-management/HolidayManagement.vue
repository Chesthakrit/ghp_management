<template>
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
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../../../api'
import Swal from 'sweetalert2'

const holidays = ref([])
const selectedYear = ref(new Date().getFullYear())

const fetchHolidays = async () => {
  try {
    const res = await api.get(`/attendance/holidays/${selectedYear.value}`)
    holidays.value = res.data || []
  } catch (err) {
    console.error(err)
  }
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
    showCancelButton: true,
    preConfirm: () => ({
      date: document.getElementById('h-date').value,
      name: document.getElementById('h-name').value
    })
  })
  if (v?.date) {
    await api.post('/attendance/holidays', { year: selectedYear.value, ...v })
    fetchHolidays()
  }
}

const deleteHoliday = async (hol) => {
  try {
    await api.delete(`/attendance/holidays/${hol.id}`)
    fetchHolidays()
  } catch (err) {
    console.error(err)
  }
}

onMounted(() => {
  fetchHolidays()
})
</script>

<style scoped>
.hol-card { height: 100%; display: flex; flex-direction: column; }
.header-flex { display: flex; align-items: center; gap: 8px; }
.select-clean { background: #f1f5f9; border: none; font-size: 0.85rem; font-weight: 800; border-radius: 6px; padding: 4px 8px; cursor: pointer; color: #1a2a3a; }
.btn-ghost-sm { border: 1px solid #e2e8f0; background: #fff; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 6px; cursor: pointer; transition: 0.2s; color: #64748b; }
.btn-ghost-sm:hover { border-color: #1a2a3a; color: #1a2a3a; }

.list-scroll-sm { max-height: 350px; overflow-y: auto; flex: 1; }
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
.empty-hint-sm { padding: 40px 20px; text-align: center; color: #94a3b8; font-size: 0.9rem; }
</style>
