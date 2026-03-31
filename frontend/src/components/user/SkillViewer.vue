<template>
  <div class="skills-view-wrapper">
    <div class="skills-list-side">
      <div class="section-card-flat no-shadow">
        <div v-if="!userSkills || userSkills.length === 0" class="no-skills-notice">
            <i class="fas fa-info-circle"></i>
            <p>No skills requirements listed for this job title yet.</p>
        </div>
        
        <template v-else>
          <!-- Overall Progress -->
          <div class="overall-progress-card">
            <div class="overall-circle">
              <svg viewBox="0 0 36 36" class="circular-chart">
                <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                <path class="circle-fill" :class="getOverallColor(overallPercent)" :stroke-dasharray="overallPercent + ', 100'" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
              </svg>
              <div class="overall-pct-text">{{ overallPercent }}%</div>
            </div>
            <div class="overall-info">
              <div class="overall-label">Overall Progress</div>
              <div class="overall-bar-track">
                <div class="overall-bar-fill" :class="getOverallColor(overallPercent)" :style="{ width: overallPercent + '%' }"></div>
              </div>
              <div class="overall-sub-text">Average of {{ userSkills.length }} skill(s)</div>
            </div>
          </div>

          <div class="skill-category-group" v-for="(skills, catName) in groupedSkills" :key="catName">
            <h4 class="category-title"># {{ catName }}</h4>
            <div class="skill-items-list">
              <div 
                v-for="skill in skills" 
                :key="skill.id" 
                class="skill-item-row"
                :class="{ 'active-selection': selectedSkill?.id === skill.id }"
              >
                <div class="skill-info-box" @click="selectSkill(skill)">
                  <div class="skill-name-text">{{ skill.name }}</div>
                </div>
                <div class="skill-progress-box">
                    <i 
                      v-if="skill.description" 
                      class="fas fa-info-circle skill-info-btn-inline" 
                      @click="selectSkill(skill)"
                      :class="{ 'active': selectedSkill?.id === skill.id }"
                      title="View Details"
                    ></i>
                    <div class="progress-bar-wrapper">
                      <div class="progress-bar-track">
                        <div 
                          class="progress-bar-fill" 
                          :style="{ width: (userEvaluations[skill.id] || 0) + '%' }"
                          :class="getProgressColor(skill.id)"
                        ></div>
                      </div>
                      <span class="progress-pct">{{ userEvaluations[skill.id] || 0 }}%</span>
                    </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Inline Detail Box (Pane ขวา) -->
    <div class="skills-detail-side">
      <div v-if="selectedSkill" class="inline-doc-card">
        <div class="doc-header-blue-small"></div>
        <div class="doc-body-inner">
          <h1 class="doc-inner-title">{{ selectedSkill.name }}</h1>
          <div class="doc-inner-section">
            <label class="doc-inner-label">DESCRIPTION / DETAILS</label>
            <div class="doc-inner-content-box" style="margin-bottom: 30px;">
              {{ selectedSkill.description || 'No detailed description available.' }}
            </div>

            <!-- Checklist Section -->
            <label v-if="selectedSkill.sub_duties?.length" class="doc-inner-label">CHECKLIST / REQUIREMENTS</label>
            <div v-if="selectedSkill.sub_duties?.length" class="sub-skills-checklist">
                <div 
                  v-for="sub in selectedSkill.sub_duties" 
                  :key="sub.id" 
                  class="checklist-item"
                  :class="{ 'is-checked': !!subEvaluations[sub.id], 'can-toggle': canEvaluate }"
                  @click="canEvaluate && toggleSubDuty(sub.id)"
                >
                  <div class="checkbox-box">
                    <i v-if="subEvaluations[sub.id]" class="fas fa-check"></i>
                  </div>
                  <div class="sub-skill-content">
                    <span class="sub-skill-name">{{ sub.name }}</span>
                    <button 
                      v-if="sub.tutorial_url" 
                      class="sub-skill-video-link" 
                      @click.stop="openVideoPlayer(sub.tutorial_url)"
                      title="รับชมวิดีโอสอนงาน"
                    >
                      <i class="fas fa-play-circle"></i> Tutorial
                    </button>
                  </div>
                </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="no-selection-placeholder">
        <i class="fas fa-book-open"></i>
        <p>เลือก Skill เพื่อดูรายละเอียดการทำงาน</p>
      </div>
    </div>

    <!-- ─── Video Player Modal (Premium Overlay) ─── -->
    <div v-if="showVideoPlayer" class="video-modal-overlay" @click.self="closeVideoPlayer">
      <div class="video-modal-container">
        <button class="video-close-btn" @click="closeVideoPlayer">×</button>
        <video 
          ref="videoElement"
          class="premium-video-player"
          controls
          autoplay
          playsinline
        >
          <source :src="currentVideoUrl" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '../../api'

const props = defineProps({
  userSkills: {
    type: Array,
    required: true
  },
  userEvaluations: {
    type: Object,
    required: true
  },
  subEvaluations: {
    type: Object,
    required: true
  },
  overallPercent: {
    type: Number,
    default: 0
  },
  selectedSkill: {
    type: Object,
    default: null
  },
  canEvaluate: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select-skill', 'toggle-sub-duty'])

// Video Player State
const showVideoPlayer = ref(false)
const currentVideoUrl = ref('')
const videoElement = ref(null)

const openVideoPlayer = (url) => {
  if (!url) return
  const apiHost = api.defaults.baseURL ? api.defaults.baseURL.replace(/\/$/, '') : 'http://localhost:8000'
  
  // 1. แปลงที่อยู่และเครื่องแม่ให้ตรงตามสถานะการใช้งาน
  let resolvedUrl = url
  if (url.startsWith('http')) {
    resolvedUrl = url.replace(/http:\/\/localhost:8000|http:\/\/127.0.0.1:8000/, apiHost)
  } else {
    // ถ้าเป็น Path สั้น ให้เติมชื่อเครื่องแม่เข้าไป
    resolvedUrl = apiHost + (url.startsWith('/') ? '' : '/') + url
  }
  
  // 2. ถ้าเจอพาร์ทเก่า (/videos/) ให้ซ่อมเป็นพาร์ทใหม่ที่มีระบบตรวจบัตร (/hr/videos/) ทันที
  if (resolvedUrl.includes('/videos/') && !resolvedUrl.includes('/hr/videos/')) {
    resolvedUrl = resolvedUrl.replace('/videos/', '/hr/videos/')
  }

  // 3. แนบกุญแจ (Token) สำหรับวิดีโอนิรภัย
  let finalUrl = resolvedUrl
  if (resolvedUrl.includes('/hr/videos/')) {
    const token = localStorage.getItem('token')
    finalUrl = resolvedUrl.includes('?') ? `${resolvedUrl}&token=${token}` : `${resolvedUrl}?token=${token}`
  }

  currentVideoUrl.value = finalUrl
  showVideoPlayer.value = true
}

const closeVideoPlayer = () => {
  if (videoElement.value) {
    videoElement.value.pause()
  }
  showVideoPlayer.value = false
  currentVideoUrl.value = ''
}

const groupedSkills = computed(() => {
  const groups = {}
  props.userSkills.forEach(s => {
    const cat = s.category?.name || 'Uncategorized'
    if (!groups[cat]) groups[cat] = []
    groups[cat].push(s)
  })
  return groups
})

const selectSkill = (skill) => {
  emit('select-skill', skill)
}

const toggleSubDuty = (subId) => {
  emit('toggle-sub-duty', subId)
}

const getProgressColor = (skillId) => {
  const pct = props.userEvaluations[skillId] || 0
  if (pct >= 80) return 'progress-green'
  if (pct >= 40) return 'progress-blue'
  if (pct > 0) return 'progress-amber'
  return ''
}

const getOverallColor = (pct) => {
  if (pct >= 80) return 'color-green'
  if (pct >= 40) return 'color-blue'
  if (pct > 0) return 'color-amber'
  return ''
}
</script>

<style scoped>
/* Overall Progress */
.overall-progress-card {
  display: flex;
  align-items: center;
  gap: 20px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.overall-circle {
  position: relative;
  width: 72px;
  height: 72px;
  flex-shrink: 0;
}

.circular-chart {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.circle-bg {
  fill: none;
  stroke: #e2e8f0;
  stroke-width: 3;
}

.circle-fill {
  fill: none;
  stroke: #94a3b8;
  stroke-width: 3;
  stroke-linecap: round;
  transition: stroke-dasharray 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.circle-fill.color-amber { stroke: #f59e0b; }
.circle-fill.color-blue { stroke: #3b82f6; }
.circle-fill.color-green { stroke: #22c55e; }

.overall-pct-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.1rem;
  font-weight: 800;
  color: #1e293b;
}

.overall-info {
  flex: 1;
}

.overall-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 8px;
}

.overall-bar-track {
  height: 10px;
  background: #e2e8f0;
  border-radius: 99px;
  overflow: hidden;
  margin-bottom: 6px;
}

.overall-bar-fill {
  height: 100%;
  border-radius: 99px;
  background: #94a3b8;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.overall-bar-fill.color-amber { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.overall-bar-fill.color-blue { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.overall-bar-fill.color-green { background: linear-gradient(90deg, #22c55e, #4ade80); }

.overall-sub-text {
  font-size: 0.75rem;
  color: #94a3b8;
}

/* Skills Section (from UserProfile.vue) */
.skills-view-wrapper {
  display: flex;
  gap: 24px;
  height: calc(100vh - 200px);
  min-height: 500px;
}

.skills-list-side {
  flex: 1;
  max-width: 450px;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding-right: 12px;
}

.skills-detail-side {
  flex: 2;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.no-skills-notice {
  text-align: center;
  padding: 40px 20px;
  color: #94a3b8;
}

.no-skills-notice i {
  font-size: 2.5rem;
  margin-bottom: 12px;
  color: #cbd5e0;
}

.no-skills-notice p {
  margin: 0;
  font-size: 0.95rem;
}

.skill-category-group {
  margin-bottom: 24px;
}

.category-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0 12px;
  margin: 0 0 12px 0;
}

.skill-items-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skill-item-row {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}

.skill-item-row:hover {
  border-color: #cbd5e0;
  box-shadow: 0 4px 6px rgba(0,0,0,0.04);
}

.skill-item-row.active-selection {
  border-color: #3b82f6;
  background: #f8fafc;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.skill-info-box {
  cursor: pointer;
}

.skill-name-text {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.95rem;
  line-height: 1.4;
}

.skill-progress-box {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #f8fafc;
  padding: 8px 12px;
  border-radius: 8px;
}

.progress-bar-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar-track {
  flex: 1;
  height: 8px;
  background: #e2e8f0;
  border-radius: 99px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 99px;
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  background: #94a3b8;
}

.progress-bar-fill.progress-amber {
  background: linear-gradient(90deg, #f59e0b, #fbbf24);
}

.progress-bar-fill.progress-blue {
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
}

.progress-bar-fill.progress-green {
  background: linear-gradient(90deg, #22c55e, #4ade80);
}

.progress-pct {
  font-size: 0.8rem;
  font-weight: 700;
  color: #475569;
  min-width: 38px;
  text-align: right;
}

.skill-info-btn-inline {
  color: #94a3b8;
  margin-right: 8px;
  cursor: pointer;
  transition: color 0.2s;
}

.skill-info-btn-inline:hover {
  color: #3b82f6;
}

.skill-info-btn-inline.active {
  color: #3b82f6;
}

.inline-doc-card {
  background: #fff;
  border-radius: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.doc-header-blue-small {
  height: 6px;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
}

.doc-body-inner {
  padding: 32px;
  overflow-y: auto;
  flex: 1;
}

.doc-inner-title {
  margin: 0 0 24px 0;
  font-size: 1.5rem;
  color: #1e293b;
  font-weight: 700;
  line-height: 1.3;
}

.doc-inner-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 700;
  color: #94a3b8;
  margin-bottom: 8px;
  letter-spacing: 0.05em;
}

.doc-inner-content-box {
  background: #f8fafc;
  padding: 20px;
  border-radius: 12px;
  color: #475569;
  line-height: 1.6;
  font-size: 0.95rem;
  border: 1px solid #e2e8f0;
}

.sub-skills-checklist {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checklist-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  transition: all 0.2s;
}

.checklist-item.can-toggle {
  cursor: pointer;
}

.checklist-item.can-toggle:hover {
  border-color: #cbd5e0;
  background: #f8fafc;
}

.checklist-item.is-checked {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.checkbox-box {
  width: 24px;
  height: 24px;
  border: 2px solid #cbd5e0;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: #fff;
  transition: all 0.2s;
  color: #fff;
}

.checklist-item.is-checked .checkbox-box {
  background: #22c55e;
  border-color: #22c55e;
}

.sub-skill-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.sub-skill-name {
  color: #334155;
  font-size: 0.95rem;
  line-height: 1.5;
  padding-top: 2px;
}

.sub-skill-video-link {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #eff6ff;
  color: #2563eb;
  padding: 4px 10px;
  border-radius: 99px;
  font-size: 0.75rem;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.2s;
  flex-shrink: 0;
  border: 1px solid #dbeafe;
}

.sub-skill-video-link:hover {
  background: #2563eb;
  color: #fff;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
}

.sub-skill-video-link i {
  font-size: 0.85rem;
}

.checklist-item.is-checked .sub-skill-name {
  color: #15803d;
  font-weight: 500;
}

.no-selection-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 16px;
  border: 1px dashed #cbd5e0;
  color: #94a3b8;
}

.no-selection-placeholder i {
  font-size: 3rem;
  margin-bottom: 16px;
  color: #e2e8f0;
}

.section-card-flat {
  background: none;
}

/* Scrollbar adjustments */
.skills-list-side::-webkit-scrollbar,
.doc-body-inner::-webkit-scrollbar {
  width: 6px;
}

.skills-list-side::-webkit-scrollbar-track,
.doc-body-inner::-webkit-scrollbar-track {
  background: transparent;
}

.skills-list-side::-webkit-scrollbar-thumb,
.doc-body-inner::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 10px;
}

.skills-list-side::-webkit-scrollbar-thumb:hover,
.doc-body-inner::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

@media (max-width: 1024px) {
  .skills-view-wrapper {
    flex-direction: column;
    height: auto;
  }
  .skills-list-side {
    max-width: none;
    height: 400px;
  }
}

/* ─── Video Player Modal Styles (Shared) ─── */
.video-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  z-index: 10000; /* ให้สูงกว่าทุกอย่างในหน้านี้ */
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.video-modal-container {
  position: relative;
  width: 100%;
  max-width: 1200px;
  max-height: 90vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.premium-video-player {
  width: 100%;
  height: auto;
  max-height: 90vh;
  outline: none;
}

.video-close-btn {
  position: absolute;
  top: 15px;
  right: 20px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 32px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  cursor: pointer;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.video-close-btn:hover {
  background: rgba(255, 255, 255, 0.4);
  transform: rotate(90deg);
}

@media (max-width: 768px) {
  .video-modal-overlay {
    padding: 10px;
    z-index: 99999;
  }
  .video-modal-container {
    max-height: 80vh;
    border-radius: 8px;
  }
  .video-close-btn {
    top: 10px;
    right: 10px;
    width: 36px;
    height: 36px;
    font-size: 24px;
  }
}

.sub-skill-video-link {
  cursor: pointer;
  border: none;
}
</style>
