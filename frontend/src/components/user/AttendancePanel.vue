<template>
  <div class="attendance-panel-container">
    <div class="attendance-header">
      
      <!-- Title and Time on the left -->
      <div class="header-titles">
        <h1>Attendance</h1>
        <div class="time-display-large">{{ currentTime }}</div>
        <div class="date-text-small">{{ currentDate }}</div>
      </div>
      
      <!-- Button on the right -->
      <div class="header-actions">
        <button class="btn-onsite-square" @click="handleOnSiteCheckin">
          <i class="fas fa-map-marker-alt"></i>
          <span>ON-SITE</span>
        </button>
      </div>

    </div>

    <div class="attendance-body">
      <p>Content for Check IN / Check OUT will be here...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// Reactive variables for time
const currentTime = ref('00:00:00')
const currentDate = ref('')
let timerInterval = null

// Function to update the clock
const updateClock = () => {
  const now = new Date()
  
  // Format time (HH:MM:SS) in English
  currentTime.value = now.toLocaleTimeString('en-US', { hour12: false })
  
  // Format date shorthand (e.g. Tue, Mar 10, 2026)
  currentDate.value = now.toLocaleDateString('en-US', { 
    weekday: 'short', 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

// Function triggered when the button is clicked
const handleOnSiteCheckin = () => {
  console.log("On-site checkin clicked")
  // Will add the logic later
}

// Start the clock when the component is mounted
onMounted(() => {
  updateClock() // Initial call to avoid showing 00:00:00 initially
  timerInterval = setInterval(updateClock, 1000) // Update every 1 second
})

// Clear the interval when user leaves the page to save memory
onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})
</script>

<style scoped>
.attendance-panel-container {
  padding: 20px;
}

.attendance-header {
  display: flex;
  justify-content: space-between; /* Push header to left and button to right */
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #ecf0f1;
}

.header-titles {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  min-width: 200px; /* Fixed width to keep things aligned */
}

.attendance-header h1 {
  margin: 0 0 5px 0;
  font-size: 1.6rem;
  color: #2c3e50;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 700;
}

.time-display-large {
  font-size: 2.8rem;
  font-weight: 800;
  font-family: 'Courier New', Courier, monospace;
  color: #2ecc71;
  line-height: 1;
  margin: 5px 0;
  letter-spacing: -1px;
}

.date-text-small {
  font-size: 0.85rem;
  color: #95a5a6;
  margin-top: 2px;
  font-weight: 500;
}

.header-actions {
  text-align: right;
}

.btn-onsite-square {
  width: 90px;
  height: 90px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f39c12;
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 10px rgba(243, 156, 18, 0.3);
  padding: 0;
}

.btn-onsite-square i {
  font-size: 1.8rem;
  margin-bottom: 5px;
}

.btn-onsite-square span {
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.5px;
}

.btn-onsite-square:hover {
  background-color: #e67e22;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(243, 156, 18, 0.4);
}

.btn-onsite-square:active {
  transform: translateY(0) scale(0.95);
}


.attendance-body {
  text-align: center;
  padding: 40px 0;
  color: #95a5a6;
}

@media (max-width: 480px) {
  .header-titles {
    min-width: 150px;
  }
  .time-display-large {
    font-size: 2rem;
  }
  .attendance-header h1 {
    font-size: 1.1rem;
  }
  .btn-onsite-square {
    width: 75px;
    height: 75px;
    border-radius: 10px;
  }
  .btn-onsite-square i {
    font-size: 1.5rem;
  }
  .btn-onsite-square span {
    font-size: 0.65rem;
  }
}
</style>
