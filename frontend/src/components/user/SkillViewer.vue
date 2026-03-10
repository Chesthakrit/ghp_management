<template>
  <div class="skills-view-wrapper">
    <div class="skills-list-side">
      <div class="section-card-flat no-shadow">
        <div v-if="!userSkills || userSkills.length === 0" class="no-skills-notice">
            <i class="fas fa-info-circle"></i>
            <p>No skills requirements listed for this job title yet.</p>
        </div>
        
        <template v-else>
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
                <div class="skill-rating-box">
                  <div class="stars-row">
                    <i 
                      v-if="skill.description" 
                      class="fas fa-info-circle skill-info-btn-inline" 
                      @click="selectSkill(skill)"
                      :class="{ 'active': selectedSkill?.id === skill.id }"
                      title="View Details"
                    ></i>
                    <i 
                      v-for="star in 5" 
                      :key="star"
                      class="fa-star"
                      :class="[getStarClass(skill.id, star), { 'clickable': canEvaluate }]"
                      @click="handleRate(skill.id, star)"
                    ></i>
                  </div>
                  <div class="rating-label">{{ getRatingLabel(skill.id) }}</div>
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
                  <span class="sub-skill-name">{{ sub.name }}</span>
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
  </div>
</template>

<script setup>
import { computed } from 'vue'

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
  selectedSkill: {
    type: Object,
    default: null
  },
  canEvaluate: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select-skill', 'toggle-sub-duty', 'handle-rate'])

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

const handleRate = (skillId, score) => {
  emit('handle-rate', skillId, score)
}

const getStarClass = (skillId, starIndex) => {
  const score = props.userEvaluations[skillId] || 0
  if (starIndex <= score) return 'fas fa-star text-gold'
  return 'far fa-star text-muted'
}

const getRatingLabel = (skillId) => {
  const score = props.userEvaluations[skillId] || 0
  if (!score) return 'Pending'
  const labels = ['Novice', 'Beginner', 'Competent', 'Proficient', 'Expert']
  return labels[score - 1] || 'Rated'
}
</script>

<style scoped>
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

.skill-rating-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f8fafc;
  padding: 8px 12px;
  border-radius: 8px;
}

.stars-row {
  display: flex;
  gap: 4px;
  align-items: center;
}

.stars-row i {
  font-size: 0.9rem;
  transition: transform 0.1s;
}

.stars-row i.clickable {
  cursor: pointer;
}

.stars-row i.clickable:hover {
  transform: scale(1.2);
}

.text-gold {
  color: #f59e0b;
  text-shadow: 0 0 2px rgba(245, 158, 11, 0.3);
}

.text-muted {
  color: #cbd5e0;
}

.rating-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 12px;
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

.sub-skill-name {
  color: #334155;
  font-size: 0.95rem;
  line-height: 1.5;
  padding-top: 2px;
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
</style>
