<template>
  <div class="hr-management-container">
    <div class="hr-settings-grid">
      <!-- 1 & 2. Unified Organization Structure (Compact) -->
      <div class="section-card org-struct-card">
        <div class="section-header">
          <h2 class="header-title">🏢 Organization & Job Titles</h2>
        </div>
        
        <!-- Global Add Dept -->
        <div class="hr-form-add main-add" v-if="hasPerm('action.hr.add_dept')">
          <input v-model="newDept.name" placeholder="New Department Name (e.g. Finance)" class="hr-input" @keyup.enter="saveDept" />
          <button class="btn-primary" @click="saveDept">+ Add Dept</button>
        </div>

        <div class="org-tree">
          <draggable
            v-model="localDepartments"
            item-key="id"
            handle=".drag-handle"
            animation="200"
            ghost-class="drag-ghost"
            @end="saveDeptOrder"
          >
            <template #item="{ element: d }">
            <div class="org-dept-block">
              <!-- Dept Header -->
              <div class="dept-row">
                <div v-if="editingDept?.id === d.id" class="edit-mode-row">
                  <input v-model="editingDept.name" class="hr-input-sm" />
                  <button class="btn-primary-xs" @click="updateDept">Save</button>
                  <button class="btn-cancel-xs" @click="editingDept = null">Cancel</button>
                </div>
                <div v-else class="view-mode-row dept-header-row" @click="toggleDeptExpansion(d.id)">
                  <div class="dept-title-content">
                    <span class="drag-handle" @click.stop title="ลากเพื่อเรียงลำดับ">≡</span>
                    <span class="toggle-icon">{{ expandedDepts.includes(d.id) ? '▼' : '▶' }}</span>
                    <span class="dept-title" @dblclick.stop="startEditDept(d)">{{ d.name }}</span>
                  </div>
                  <div class="dept-actions" @click.stop>
                    <button v-if="hasPerm('action.hr.delete')" class="action-icon-btn delete" @click="deleteDept(d.id)" title="Delete Dept">🗑️</button>
                  </div>
                </div>
              </div>

              <!-- Job Titles List under Dept -->
              <div v-if="expandedDepts.includes(d.id)" class="jt-container">
                <draggable
                  :model-value="localJobTitles.filter(j => j.department_id === d.id)"
                  @update:model-value="val => updateJTOrder(val, d.id)"
                  item-key="id"
                  handle=".drag-handle-jt"
                  animation="200"
                  ghost-class="drag-ghost"
                  @end="evt => saveJTOrder(d.id)"
                >
                  <template #item="{ element: jt }">
                  <div class="jt-block-nested">
                    <div v-if="editingJT?.id === jt.id" class="edit-mode-row">
                      <input v-model="editingJT.name" class="hr-input-sm" />
                      <button class="btn-primary-xs" @click="updateJT">Save</button>
                      <button class="btn-cancel-xs" @click="editingJT = null">Cancel</button>
                    </div>
                    <div v-else class="view-mode-row jt-main-row" @click="toggleJTExpansion(jt.id)">
                      <div class="jt-title-content">
                        <span class="drag-handle-jt" @click.stop title="ลากเพื่อเรียงลำดับ">≡</span>
                        <span class="toggle-icon-sm">{{ expandedJTs.includes(jt.id) ? '▼' : '▶' }}</span>
                        <span class="jt-name" @dblclick.stop="startEditJT(jt)">{{ jt.name }}</span>
                      </div>
                      <div class="jt-actions" @click.stop>
                        <button v-if="hasPerm('action.hr.manage_jt_skills')" class="btn-action-pill" @click="openJDModal(jt)">Skills</button>
                        <button v-if="hasPerm('action.hr.delete')" class="action-icon-btn delete" @click="deleteJT(jt.id)">🗑️</button>
                      </div>
                    </div>
                    <!-- Skill Preview under JT -->
                    <div v-if="expandedJTs.includes(jt.id)" class="jt-skill-preview">
                       <div v-if="jt.duties && jt.duties.length > 0" class="jt-skill-list">
                          <div v-for="duty in jt.duties" :key="duty.id" class="jt-skill-item">
                             {{ duty.name }}
                          </div>
                       </div>
                       <div v-else class="no-data-hint-sm jt-no-skill-hint">
                          No skills assigned yet.
                       </div>
                 </div>
                                    </div>
                   </template>
                </draggable>

                <!-- Quick Add JT for this Dept -->
                <div class="quick-add-jt" v-if="hasPerm('action.hr.add_jt')">
                  <input 
                    v-model="newJobTitle.name" 
                    v-if="selectedDeptId === d.id"
                    placeholder="Enter job title..." 
                    class="hr-input-sm"
                    @keyup.enter="saveJT"
                    autofocus
                  />
                  <button 
                    v-if="selectedDeptId !== d.id"
                    class="btn-ghost-add" 
                    @click="selectedDeptId = d.id; newJobTitle.name = ''"
                  >
                    + Add Job Title
                  </button>
                  <div v-else class="quick-add-actions">
                     <button class="btn-primary-xs" @click="saveJT">Add</button>
                     <button class="btn-cancel-xs" @click="selectedDeptId = null">Cancel</button>
                  </div>
                </div>
              </div>
            </div>
            </template>
          </draggable>
        </div>
      </div>
      <div class="section-card skill-mgmt-card">
        <div class="section-header">
          <h2 class="header-title">📚 Skills & Category Library</h2>
        </div>
        
        <!-- Global Add Tag -->
        <div class="hr-form-add main-add" v-if="hasPerm('action.hr.add_tag')">
          <input v-model="newDutyCategoryName" placeholder="New Skill Tag (e.g. Software)" class="hr-input" @keyup.enter="saveDutyCategory" />
          <button class="btn-primary" @click="saveDutyCategory">+ Add Tag</button>
        </div>

        <div class="org-tree">
          <!-- Uncategorized Block -->
          <div v-if="dutiesPool.filter(d => !d.category_id).length > 0" class="org-dept-block uncategorized">
             <div class="dept-row uncat-skill-row" @click="toggleDeptExpansion('uncat_skill')">
               <div class="dept-title-content">
                 <span class="toggle-icon">{{ expandedDepts.includes('uncat_skill') ? '▼' : '▶' }}</span>
                 <span class="dept-title">Uncategorized Skills</span>
               </div>
             </div>
             <div v-if="expandedDepts.includes('uncat_skill')" class="jt-container">
                <draggable
                  :model-value="dutiesPool.filter(d => !d.category_id)"
                  @update:model-value="val => updateDutyOrderLocal(val, null)"
                  item-key="id"
                  handle=".drag-handle-skill"
                  animation="200"
                  ghost-class="drag-ghost"
                  @end="evt => saveDutyOrder(null)"
                >
                  <template #item="{ element: duty }">
                  <div class="skill-block-nested">
                    <div class="skill-main-row clickable-row" @click="toggleDutyExpansion(duty.id)">
                       <div class="jt-title-content">
                          <span class="drag-handle-skill" @click.stop title="ลากเพื่อเรียงลำดับ">≡</span>
                          <span class="toggle-icon-sm">{{ expandedDuties.includes(duty.id) ? '▾' : '▸' }}</span>
                          <span class="jt-name" @dblclick.stop="openDutyModal(duty)">{{ duty.name }}</span>
                       </div>
                       <div class="jt-actions" @click.stop>
                          <button v-if="hasPerm('action.hr.edit_skill')" class="action-icon-btn" @click="openDutyModal(duty)" title="Edit Skill">⚙️</button>
                          <button v-if="hasPerm('action.hr.delete_skill')" class="action-icon-btn delete" @click="deleteDutyFromPool(duty.id)" title="Delete Skill">🗑️</button>
                       </div>
                    </div>
                    <!-- Sub-skills & Desc -->
                    <div v-if="expandedDuties.includes(duty.id)" class="skill-details-area">
                       <div class="skill-details-grid">
                          <div class="skill-desc-container">
                             <span class="detail-label">Description</span>
                             <p class="skill-desc-text">{{ duty.description || 'No description provided.' }}</p>
                          </div>
                          <div class="skill-sub-container">
                             <span class="detail-label">Sub-skills ({{ duty.sub_duties?.length || 0 }})</span>
                             <div class="sub-skills-dropdown-list">
                                <draggable
                                  v-model="duty.sub_duties"
                                  item-key="id"
                                  handle=".drag-handle-sub"
                                  animation="200"
                                  ghost-class="drag-ghost"
                                  @end="saveSubDutyOrder(duty.id)"
                                >
                                  <template #item="{ element: sub }">
                                  <div class="sub-skill-dropdown-item">
                                    <div class="sub-skill-dropdown-header" @click.stop="toggleSubDutyExpansion(sub.id)">
                                      <span class="drag-handle-sub" @click.stop title="ลากเพื่อเรียงลำดับ">≡</span>
                                      <span class="sub-dd-toggle">{{ expandedSubDuties.includes(sub.id) ? '▾' : '▸' }}</span>
                                      <span class="sub-dd-name">{{ sub.name }}</span>
                                      <span v-if="sub.tutorial_url" class="sub-dd-video-dot" title="มีวิดีโอ">📹</span>
                                    </div>
                                    <div v-if="expandedSubDuties.includes(sub.id)" class="sub-skill-dropdown-body">
                                      <div v-if="sub.tutorial_url" class="sub-dd-video-row">
                                        <span class="sub-dd-label">🎬 วิดีโอสอน:</span>
                                        <button class="sub-dd-play-btn" @click.stop="openVideoPlayer(sub.tutorial_url)">▶ เล่นวิดีโอ</button>
                                      </div>
                                      <div v-else class="sub-dd-no-video">ไม่มีวิดีโอประกอบ</div>
                                    </div>
                                  </div>
                                  </template>
                                </draggable>
                                <div v-if="!duty.sub_duties?.length" class="no-sub-hint">No checklist defined</div>
                             </div>
                          </div>
                       </div>
                    </div>
                  </div>
                  </template>
                </draggable>
             </div>
          </div>

          <!-- Categorized Blocks -->
          <div v-for="cat in dutyCategories" :key="cat.id" class="org-dept-block">
            <!-- Tag Header -->
            <div class="dept-row cat-header-row" @click="toggleDeptExpansion('cat_' + cat.id)">
              <div v-if="editingDutyCategory?.id === cat.id" class="edit-mode-row" @click.stop>
                <input v-model="editingDutyCategory.name" class="hr-input-sm" />
                <button class="btn-primary-xs" @click="updateDutyCategory">Save</button>
                <button class="btn-cancel-xs" @click="editingDutyCategory = null">Cancel</button>
              </div>
              <div v-else class="view-mode-row">
                <div class="dept-title-content">
                  <span class="toggle-icon">{{ expandedDepts.includes('cat_' + cat.id) ? '▼' : '▶' }}</span>
                  <span class="dept-title" @dblclick.stop="startEditDutyCategory(cat)">{{ cat.name }}</span>
                </div>
                <div class="dept-actions" @click.stop>
                  <button v-if="hasPerm('action.hr.delete_tag')" class="action-icon-btn delete" @click="deleteDutyCategory(cat.id)" title="Delete Tag">🗑️</button>
                </div>
              </div>
            </div>

            <!-- Skills List under Tag -->
            <div v-if="expandedDepts.includes('cat_' + cat.id)" class="jt-container">
                <draggable
                   :model-value="dutiesPool.filter(d => d.category_id === cat.id)"
                   @update:model-value="val => updateDutyOrderLocal(val, cat.id)"
                   item-key="id"
                   handle=".drag-handle-skill"
                   animation="200"
                   ghost-class="drag-ghost"
                   @end="evt => saveDutyOrder(cat.id)"
                >
                  <template #item="{ element: duty }">
                  <div class="skill-block-nested">
                <div class="skill-main-row clickable-row" @click="toggleDutyExpansion(duty.id)">
                   <div class="jt-title-content">
                          <span class="drag-handle-skill" @click.stop title="ลากเพื่อเรียงลำดับ">≡</span>
                          <span class="toggle-icon-sm">{{ expandedDuties.includes(duty.id) ? '▾' : '▸' }}</span>
                      <span class="jt-name" @dblclick.stop="openDutyModal(duty)">{{ duty.name }}</span>
                   </div>
                   <div class="jt-actions" @click.stop>
                      <button v-if="hasPerm('action.hr.edit_skill')" class="action-icon-btn" @click="openDutyModal(duty)" title="Edit Skill">⚙️</button>
                      <button v-if="hasPerm('action.hr.delete_skill')" class="action-icon-btn delete" @click="deleteDutyFromPool(duty.id)" title="Delete Skill">🗑️</button>
                   </div>
                </div>

                <!-- Sub-skills & Desc -->
                <div v-if="expandedDuties.includes(duty.id)" class="skill-details-area">
                   <div class="skill-details-grid">
                      <div class="skill-desc-container">
                         <span class="detail-label">Description</span>
                         <p class="skill-desc-text">{{ duty.description || 'No description provided.' }}</p>
                      </div>
                      <div class="skill-sub-container">
                         <span class="detail-label">Sub-skills ({{ duty.sub_duties?.length || 0 }})</span>
                         <div class="sub-skills-dropdown-list">
                             <draggable
                               v-model="duty.sub_duties"
                               item-key="id"
                               handle=".drag-handle-sub"
                               animation="200"
                               ghost-class="drag-ghost"
                               @end="saveSubDutyOrder(duty.id)"
                             >
                               <template #item="{ element: sub }">
                               <div class="sub-skill-dropdown-item">

                              <div class="sub-skill-dropdown-header" @click.stop="toggleSubDutyExpansion(sub.id)">
                                    <span class="drag-handle-sub" @click.stop title="ลากเพื่อเรียงลำดับ">≡</span>
                                    <span class="sub-dd-toggle">{{ expandedSubDuties.includes(sub.id) ? '▾' : '▸' }}</span>

                                <span class="sub-dd-name">{{ sub.name }}</span>

                                <span v-if="sub.tutorial_url" class="sub-dd-video-dot" title="มีวิดีโอ">📹</span>

                              </div>

                              <div v-if="expandedSubDuties.includes(sub.id)" class="sub-skill-dropdown-body">

                                <div v-if="sub.tutorial_url" class="sub-dd-video-row">

                                  <span class="sub-dd-label">🎬 วิดีโอสอน:</span>

                                  <button class="sub-dd-play-btn" @click.stop="openVideoPlayer(sub.tutorial_url)">▶ เล่นวิดีโอ</button>

                                </div>

                                <div v-else class="sub-dd-no-video">ไม่มีวิดีโอประกอบ</div>

                              </div>

                            </div>
                               </template>
                             </draggable>
                             <div v-if="!duty.sub_duties?.length" class="no-sub-hint">No checklist defined</div>

                         </div>
                      </div>
                   </div>
                </div>
              </div>
                  </template>
                </draggable>
              </div>

              <!-- Quick Add Skill for this Tag -->
              <div class="quick-add-jt" v-if="hasPerm('action.hr.add_skill')">
                <input 
                  v-model="newDutyName" 
                  v-if="selectedSkillCatId === 'tag_' + cat.id"
                  placeholder="Enter skill name..." 
                  class="hr-input-sm"
                  @keyup.enter="saveNewDutyWithCat(cat.id)"
                  autofocus
                />
                <button 
                  v-if="selectedSkillCatId !== 'tag_' + cat.id"
                  class="btn-ghost-add" 
                  @click="selectedSkillCatId = 'tag_' + cat.id; newDutyName = ''"
                >
                  + Add Skill to {{ cat.name }}
                </button>
                <div v-else class="quick-add-actions">
                   <button class="btn-primary-xs" @click="saveNewDutyWithCat(cat.id)">Add</button>
                   <button class="btn-cancel-xs" @click="selectedSkillCatId = null">Cancel</button>
                </div>
              </div>
            </div>

            <!-- ─── Modals (Skills, JD, Page Access) ─── -->
    <div v-if="showDutyModal" class="modal-overlay" @click.self="closeDutyModal">
      <div class="modal-box jd-modal">
        <h3 class="modal-title">Skill Details</h3>
        <div class="form-group"><label>Skill Name</label><input v-model="selectedDuty.name" class="form-input" /></div>
        <div class="form-group"><label>Category / Tag</label>
          <select v-model="selectedDuty.category_id" class="form-input">
            <option :value="null">None / Uncategorized</option>
            <option v-for="cat in dutyCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </div>
        <div class="form-group"><label>Description</label><textarea v-model="selectedDuty.description" class="form-input" rows="3"></textarea></div>
        <div class="sub-skills-section">
          <label class="form-label-checklist">เพิ่มสกิลย่อย (CHECKLIST)</label>
          <div class="add-sub-skill-form">
            <div class="add-sub-inputs">
              <input v-model="newSubDutyName" class="form-input" placeholder="ชื่อสกิลย่อย..." @keyup.enter="addSubDuty" />
              <input v-model="newSubDutyUrl" class="form-input form-input-sm" placeholder="🔗 URL วิดีโอสอน (ไม่บังคับ)" />
            </div>
            <button class="btn-primary btn-add-sub" @click="addSubDuty">+ เพิ่ม</button>
          </div>
          <div class="sub-skills-list-admin">
             <div v-for="sub in selectedDuty.sub_duties" :key="sub.id" class="sub-skill-admin-item">
                <div class="sub-skill-info">
                  <span class="sub-skill-name-text">{{ sub.name }}</span>
                  <span v-if="sub.tutorial_url" class="video-status-badge has-video">📹 มีวิดีโอ</span>
                  <span v-else class="video-status-badge no-video">ไม่มีวิดีโอ</span>
                </div>
                <div class="sub-skill-actions">
                  <button v-if="sub.tutorial_url" class="btn-action-sm btn-video" @click="openVideoPlayer(sub.tutorial_url)" title="ดูวิดีโอสอน">🎬</button>
                  <button class="btn-action-sm btn-edit-link" @click="promptTutorialUrl(sub)" title="แก้ไขลิงก์วิดีโอ">✏️</button>
                  <button class="btn-action-sm btn-trash" @click="removeSubDuty(sub.id)" title="ลบ">🗑️</button>
                </div>
             </div>
          </div>
        </div>
        <div class="modal-actions"><button class="btn-cancel" @click="closeDutyModal">Cancel</button><button class="btn-primary" @click="saveDutyDetails">Save Details</button></div>
      </div>
    </div>

    <div v-if="showJDModal" class="modal-overlay" @click.self="closeJDModal">
      <div class="modal-box jd-modal">
        <h3 class="modal-title">Skills for {{ selectedJT?.name }}</h3>
        <div class="hr-list jd-list scrollable-list">
          <label v-for="duty in dutiesPool" :key="duty.id" class="hr-list-item skill-assign-item">
            <input type="checkbox" v-model="selectedJT_duties" :value="duty.id" class="assign-checkbox" />
            <span class="hr-label">{{ duty.name }}</span>
          </label>
        </div>
        <div class="modal-actions"><button class="btn-cancel" @click="closeJDModal">Cancel</button><button class="btn-primary" @click="saveJT_Duties">Save Assignments</button></div>
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
    </div>
  </div>
</div>

</template>
<script setup>

import { ref, watch, onMounted } from 'vue'
import api from '../../api'
import Swal from 'sweetalert2'
import draggable from 'vuedraggable'

const props = defineProps({
  departments: { type: Array, default: () => [] },
  jobTitles: { type: Array, default: () => [] },
  currentUser: { type: Object, default: () => ({}) },
  isAdmin: { type: Boolean, default: false }
})

const emit = defineEmits(['refresh'])


const hasPerm = (p) => {
  if (props.isAdmin) return true
  return (props.currentUser?.permissions || []).includes(p)
}

// All HR Logic (Refs & Methods)
const expandedDepts = ref([])
const expandedJTs = ref([])
const expandedDuties = ref([])
const expandedSubDuties = ref([])

// Shared refs across tabs, but local to this component for DND
const localDepartments = ref([...props.departments])
const localJobTitles = ref([...props.jobTitles])

watch(() => props.departments, (newVal) => {
  localDepartments.value = [...newVal]
}, { deep: true })

watch(() => props.jobTitles, (newVal) => {
  localJobTitles.value = [...newVal]
}, { deep: true })

const selectedDeptId = ref(null)
const newDept = ref({ name: '' })
const editingDept = ref(null)
const newJobTitle = ref({ name: '', department_id: null })
const editingJT = ref(null)

const dutiesPool = ref([])
const dutyCategories = ref([])
const newDutyName = ref('')
const newDutyCategoryName = ref('')
const editingDutyCategory = ref(null)

const showDutyModal = ref(false)
const selectedDuty = ref({ id: null, name: '', description: '', category_id: null, sub_duties: [] })
const newSubDutyName = ref('')
const newSubDutyUrl = ref('')
const selectedSkillCatId = ref(null)

const showJDModal = ref(false)
const selectedJT = ref(null)
const selectedJT_duties = ref([])

// Video Player State
const showVideoPlayer = ref(false)
const currentVideoUrl = ref('')
const videoElement = ref(null)

const openVideoPlayer = (url) => {
  if (!url) return
  const apiHost = api.defaults.baseURL ? api.defaults.baseURL.replace(/\/$/, '') : 'http://localhost:8000'
  
  // 1. แปลงที่อยู่และเครื่องแม่ให้ตรงตามสถานะปัจจุบัน
  let resolvedUrl = url
  if (url.startsWith('http')) {
    resolvedUrl = url.replace(/http:\/\/localhost:8000|http:\/\/127.0.0.1:8000/, apiHost)
  } else {
    // ถ้าเป็น Path สั้น ให้ต่อชื่อเครื่องแม่เข้าไป
    resolvedUrl = apiHost + (url.startsWith('/') ? '' : '/') + url
  }
  
  // 2. ถ้าเจอพาร์ทเก่า (/videos/) ให้ซ่อมเป็นพาร์ทใหม่ (/hr/videos/) ทันที
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

onMounted(() => {
  fetchHRData()
})

const fetchHRData = async () => {
  try {
    const [dutiesRes, catsRes] = await Promise.all([
      api.get('/hr/duties'),
      api.get('/hr/duty-categories')
    ])
    dutiesPool.value = dutiesRes.data
    dutyCategories.value = catsRes.data
  } catch (e) { console.error(e) }
}


// CRUD Methods
const toggleDeptExpansion = (id) => {
  if (expandedDepts.value.includes(id)) expandedDepts.value = expandedDepts.value.filter(i => i !== id)
  else expandedDepts.value.push(id)
}
const toggleJTExpansion = (id) => {
  if (expandedJTs.value.includes(id)) expandedJTs.value = expandedJTs.value.filter(i => i !== id)
  else expandedJTs.value.push(id)
}
const toggleDutyExpansion = (id) => {
  if (expandedDuties.value.includes(id)) expandedDuties.value = expandedDuties.value.filter(i => i !== id)
  else expandedDuties.value.push(id)
}
const toggleSubDutyExpansion = (id) => {
  if (expandedSubDuties.value.includes(id)) expandedSubDuties.value = expandedSubDuties.value.filter(i => i !== id)
  else expandedSubDuties.value.push(id)
}

const saveDept = async () => {
  if (!newDept.value.name) return
  try {
    const value = newDept.value.name.toLowerCase().trim().replace(/\s+/g, '_')
    await api.post('/hr/departments', { name: newDept.value.name, value: value })
    newDept.value.name = ''
    emit('refresh')
  } catch (e) { Swal.fire('Error', 'Failed to add dept', 'error') }
}

const startEditDept = (dept) => { editingDept.value = { ...dept } }
const updateDept = async () => {
  if (!editingDept.value || !editingDept.value.name) return
  try {
    const value = editingDept.value.name.toLowerCase().trim().replace(/\s+/g, '_')
    await api.put(`/hr/departments/${editingDept.value.id}`, { name: editingDept.value.name, value: value })
    editingDept.value = null
    emit('refresh')
  } catch (e) { Swal.fire('Error', 'Failed to update dept', 'error') }
}

const deleteDept = async (id) => {
  const res = await Swal.fire({ title: 'Delete?', icon: 'warning', showCancelButton: true })
  if (!res.isConfirmed) return
  try {
    await api.delete(`/hr/departments/${id}`)
    emit('refresh')
  } catch (e) { Swal.fire('Error', 'Delete failed', 'error') }
}

const saveJT = async () => {
  if (!newJobTitle.value.name || !selectedDeptId.value) return
  try {
    await api.post('/hr/job-titles', { name: newJobTitle.value.name, department_id: selectedDeptId.value })
    newJobTitle.value.name = ''
    selectedDeptId.value = null
    emit('refresh')
  } catch (e) { Swal.fire('Error', 'Add JT failed', 'error') }
}

const startEditJT = (jt) => { editingJT.value = { ...jt } }
const updateJT = async () => {
  if (!editingJT.value || !editingJT.value.name) return
  try {
    await api.put(`/hr/job-titles/${editingJT.value.id}`, { name: editingJT.value.name, department_id: editingJT.value.department_id })
    editingJT.value = null
    emit('refresh')
  } catch (e) { Swal.fire('Error', 'Update JT failed', 'error') }
}

const deleteJT = async (id) => {
  const res = await Swal.fire({ title: 'Delete?', icon: 'warning', showCancelButton: true })
  if (!res.isConfirmed) return
  try {
    await api.delete(`/hr/job-titles/${id}`)
    emit('refresh')
  } catch (e) { Swal.fire('Error', 'Delete failed', 'error') }
}

const saveDeptOrder = async () => {
  try {
    const rawList = JSON.parse(JSON.stringify(localDepartments.value))
    const items = rawList
      .filter(d => d && d.id)
      .map((d, index) => ({ 
        id: Number(d.id), 
        display_order: index + 1 
      }))
    if (items.length === 0) return
    await api.put('/hr/departments/reorder', { items })
    Swal.fire({ title: 'Reordered!', icon: 'success', toast: true, position: 'top-end', showConfirmButton: false, timer: 2000 })
    emit('refresh')
  } catch (e) { 
    console.error(e)
    Swal.fire('Error', 'Failed to save order', 'error')
  }
}

const updateJTOrder = (newList, deptId) => {
  const others = localJobTitles.value.filter(j => j.department_id !== deptId)
  localJobTitles.value = [...others, ...newList]
}

const saveJTOrder = async (deptId) => {
  try {
    const rawList = JSON.parse(JSON.stringify(localJobTitles.value))
    const deptJTs = rawList.filter(j => j.department_id === deptId && j.id)
    const items = deptJTs.map((jt, index) => ({ 
      id: Number(jt.id), 
      display_order: index + 1 
    }))
    if (items.length === 0) return
    await api.put('/hr/job-titles/reorder', { items })
    Swal.fire({ title: 'Reordered!', icon: 'success', toast: true, position: 'top-end', showConfirmButton: false, timer: 2000 })
    emit('refresh')
  } catch (e) { 
    console.error(e)
    Swal.fire('Error', 'Failed to save order', 'error')
  }
}

const saveDutyCategory = async () => {
  if (!newDutyCategoryName.value) return
  try {
    await api.post('/hr/duty-categories', { name: newDutyCategoryName.value })
    newDutyCategoryName.value = ''
    await fetchHRData()
  } catch (e) { Swal.fire('Error', 'Add category failed', 'error') }
}
const startEditDutyCategory = (cat) => { editingDutyCategory.value = { ...cat } }
const updateDutyCategory = async () => {
  if (!editingDutyCategory.value) return
  try {
    await api.put(`/hr/duty-categories/${editingDutyCategory.value.id}`, { name: editingDutyCategory.value.name })
    editingDutyCategory.value = null
    await fetchHRData()
  } catch (e) { Swal.fire('Error', 'Update failed', 'error') }
}
const deleteDutyCategory = async (id) => {
  const res = await Swal.fire({ title: 'Delete?', icon: 'warning', showCancelButton: true })
  if (!res.isConfirmed) return
  try {
    await api.delete(`/hr/duty-categories/${id}`)
    await fetchHRData()
  } catch (e) { Swal.fire('Error', 'Delete failed', 'error') }
}

const saveNewDutyWithCat = async (catId) => {
  if (!newDutyName.value) return
  try {
    await api.post('/hr/duties', { name: newDutyName.value, category_id: catId })
    newDutyName.value = ''
    selectedSkillCatId.value = null
    await fetchHRData()
  } catch (e) { Swal.fire('Error', 'Add skill failed', 'error') }
}

const updateDutyOrderLocal = (newList, catId) => {
  // Update only the items for this specific category in the main pool
  const otherCats = dutiesPool.value.filter(d => d.category_id !== catId)
  dutiesPool.value = [...otherCats, ...newList]
}

const saveDutyOrder = async (catId) => {
  try {
    const rawList = JSON.parse(JSON.stringify(dutiesPool.value))
    // Only items belonging to THIS category (or null if uncat)
    const catItems = rawList.filter(d => d.category_id === catId && d.id)
    const items = catItems.map((d, index) => ({ 
      id: Number(d.id), 
      display_order: index + 1 
    }))
    if (items.length === 0) return
    await api.put('/hr/duties/reorder', { items })
    Swal.fire({ title: 'Skills Reordered!', icon: 'success', toast: true, position: 'top-end', showConfirmButton: false, timer: 2000 })
    // fetchHRData() Not strictly needed if local state is OK, but safer
    await fetchHRData() 
  } catch (e) { 
    console.error(e)
    Swal.fire('Error', 'Failed to save skill order', 'error')
  }
}

const saveSubDutyOrder = async (dutyId) => {
  try {
    const duty = dutiesPool.value.find(d => d.id === dutyId)
    if (!duty || !duty.sub_duties) return
    const items = duty.sub_duties.map((s, index) => ({ 
      id: Number(s.id), 
      display_order: index + 1 
    }))
    if (items.length === 0) return
    await api.put('/hr/sub-duties/reorder', { items })
    Swal.fire({ title: 'Sub-skills Reordered!', icon: 'success', toast: true, position: 'top-end', showConfirmButton: false, timer: 2000 })
    await fetchHRData() 
  } catch (e) { 
    console.error(e)
    Swal.fire('Error', 'Failed to save sub-skill order', 'error')
  }
}

// Duty Modal
const openDutyModal = (duty) => {
  selectedDuty.value = { ...duty, sub_duties: duty.sub_duties ? [...duty.sub_duties] : [] }
  showDutyModal.value = true
}
const closeDutyModal = () => { showDutyModal.value = false }
const saveDutyDetails = async () => {
  try {
    await api.put(`/hr/duties/${selectedDuty.value.id}`, {
      name: selectedDuty.value.name,
      description: selectedDuty.value.description,
      category_id: selectedDuty.value.category_id
    })
    closeDutyModal()
    await fetchHRData()
    emit('refresh')
  } catch (e) { Swal.fire('Error', 'Save failed', 'error') }
}
const deleteDutyFromPool = async (id) => {
  const res = await Swal.fire({ title: 'Delete?', icon: 'warning', showCancelButton: true })
  if (!res.isConfirmed) return
  try {
    await api.delete(`/hr/duties/${id}`)
    await fetchHRData()
    emit('refresh')
  } catch (e) { Swal.fire('Error', 'Delete failed', 'error') }
}

const addSubDuty = async () => {
  if (!newSubDutyName.value || !selectedDuty.value?.id) return
  
  let processedUrl = newSubDutyUrl.value.trim()
  if (processedUrl) {
    const localPath = 'C:/Users/mangc/Desktop/Allvideo/Basic_Com/'.toLowerCase()
    const filePrefix = 'file:///C:/Users/mangc/Desktop/Allvideo/Basic_Com/'.toLowerCase()
    let lowerUrl = processedUrl.toLowerCase().replace(/\\/g, '/')
    
    if (lowerUrl.startsWith(filePrefix)) {
      processedUrl = 'http://localhost:8000/videos/' + processedUrl.substring(filePrefix.length)
    } else if (lowerUrl.startsWith(localPath)) {
      processedUrl = 'http://localhost:8000/videos/' + processedUrl.substring(localPath.length)
    }
    processedUrl = processedUrl.replace(/ /g, '%20')
  }

  try {
    await api.post('/hr/sub-duties', { 
      name: newSubDutyName.value, 
      duty_id: selectedDuty.value.id,
      tutorial_url: processedUrl || null
    })
    newSubDutyName.value = ''
    newSubDutyUrl.value = ''
    const res = await api.get(`/hr/duties/${selectedDuty.value.id}`)
    selectedDuty.value.sub_duties = res.data.sub_duties
  } catch (e) { 
    console.error(e)
    Swal.fire('Error', 'Add sub skill failed', 'error') 
  }
}
const removeSubDuty = async (id) => {
  try {
    await api.delete(`/hr/sub-duties/${id}`)
    selectedDuty.value.sub_duties = selectedDuty.value.sub_duties.filter(s => s.id !== id)
  } catch (e) { Swal.fire('Error', 'Delete failed', 'error') }
}

const promptTutorialUrl = async (sub) => {
  const { value: rawUrl, isDenied } = await Swal.fire({
    title: 'เพิ่มลิงก์วิดีโอสอน',
    input: 'text',
    inputLabel: `สำหรับ: ${sub.name}`,
    inputPlaceholder: 'ใส่ URL หรือ Path ไฟล์วิดีโอ (เช่น file:///C:/...)',
    inputValue: sub.tutorial_url || '',
    showCancelButton: true,
    showDenyButton: true,
    confirmButtonText: 'บันทึก',
    denyButtonText: '📁 เลือกไฟล์วิดีโอจากเครื่อง',
    cancelButtonText: 'ยกเลิก',
    preConfirm: (value) => {
      if (!value) return value
      let processed = value.trim()
      const markdownRegex = /!\[.*\]\((.*)\)/
      const match = processed.match(markdownRegex)
      if (match) processed = match[1]

      // ดึง Base URL จาก config (เพื่อให้มือถือเข้าถึงได้ตาม IP ใน .env)
      const apiHost = api.defaults.baseURL ? api.defaults.baseURL.replace(/\/$/, '') : 'http://localhost:8000'

      if (processed.includes('/uploads/videos/')) {
        processed = processed.replace(/.*\/uploads\/videos\//, `${apiHost}/hr/videos/`)
      }
      
      if (processed.includes('/videos/') && !processed.includes('/hr/videos/')) {
        processed = processed.replace('/videos/', '/hr/videos/')
      }

      if (processed.toLowerCase().startsWith('file:///') || processed.includes(':\\')) {
        const fileName = processed.split(/[/\\]/).pop()
        processed = `${apiHost}/hr/videos/${fileName}`
      }
      
      // ถ้าเคยวางเป็น localhost หรือ IP อื่นมา ให้แก้ให้ตรงกับที่ใช้ปัจจุบัน
      if (processed.includes('localhost:8000') || processed.includes('127.0.0.1:8000')) {
        processed = processed.replace(/http:\/\/localhost:8000|http:\/\/127.0.0.1:8000/, apiHost)
      }

      return processed.replace(/%20/g, ' ')
    }
  })

  // หน้าคนกดปุ่ม "เลือกไฟล์จากเครื่อง"
  if (isDenied) {
    const { value: file } = await Swal.fire({
      title: 'เลือกวิดีโอ',
      input: 'file',
      inputAttributes: {
        'accept': 'video/*',
        'aria-label': 'Upload tutorial video'
      },
      showCancelButton: true
    })

    if (file) {
      Swal.fire({
        title: 'กำลังอัปโหลด...',
        allowOutsideClick: false,
        didOpen: () => { Swal.showLoading() }
      })

      const formData = new FormData()
      formData.append('file', file)

      try {
        const res = await api.post('/hr/upload-video', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        // หลังจากอัปโหลดเสร็จ ให้เด้งหน้าต่างเดิมกลับมาพร้อมใส่ URL ใหม่ให้
        sub.tutorial_url = res.data.url
        return promptTutorialUrl(sub)
      } catch (e) {
        Swal.fire('Error', 'ไม่สามารถอัปโหลดไฟล์ได้', 'error')
      }
    } else {
      // ถ้ากดยกเลิกในหน้าเลือกไฟล์ ให้กลับมาหน้าหลัก
      return promptTutorialUrl(sub)
    }
  }

  if (rawUrl === undefined) return // กดยกเลิก
  
  // เข้ารหัส URL ให้ถูกต้องก่อนส่ง
  const encodedUrl = rawUrl.startsWith('http') ? rawUrl.replace(/ /g, '%20') : rawUrl
  try {
    await api.put(`/hr/sub-duties/${sub.id}`, { tutorial_url: encodedUrl })
    sub.tutorial_url = encodedUrl
    Swal.fire({ title: 'บันทึกลิงก์เรียบร้อย!', icon: 'success', toast: true, position: 'top-end', showConfirmButton: false, timer: 2000 })
  } catch (e) {
    Swal.fire('Error', 'Failed to save URL', 'error')
  }
}

// JD Modal
const openJDModal = (jt) => {
  selectedJT.value = jt
  selectedJT_duties.value = jt.duties ? jt.duties.map(d => d.id) : []
  showJDModal.value = true
}
const closeJDModal = () => { showJDModal.value = false }
const saveJT_Duties = async () => {
  try {
    await api.put(`/hr/job-titles/${selectedJT.value.id}/duties`, { duty_ids: selectedJT_duties.value })
    closeJDModal()
    emit('refresh')
  } catch (e) { Swal.fire('Error', 'Save failed', 'error') }
}


</script>

<style scoped>
.hr-management-container {
  padding: 0;
}

.hr-settings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: start;
}

.section-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.section-header {
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 15px;
  margin-bottom: 15px;
}

.header-title {
  margin: 0;
  font-size: 1.25rem;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Forms */
.hr-form-add {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.hr-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #dde3e8;
  border-radius: 8px;
  outline: none;
  font-size: 0.9rem;
}

.hr-input:focus {
  border-color: #3b82f6;
}

.hr-input-sm {
  padding: 6px 10px;
  border: 1px solid #dde3e8;
  border-radius: 6px;
  font-size: 0.85rem;
  width: 100%;
}

/* Tree Structure */
.org-tree {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.org-dept-block {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
  background: #f1f5f9;
  transition: box-shadow 0.2s;
  margin-bottom: 8px;
}

.org-dept-block:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.dept-row {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  padding: 14px 18px;
  border-bottom: 1px solid #1e293b;
}

.dept-row .dept-title {
  color: #f1f5f9 !important;
  font-size: 1rem;
}

.dept-row .toggle-icon {
  color: #94a3b8 !important;
}

.dept-row .drag-handle {
  color: #64748b !important;
}

.dept-row .action-icon-btn {
  color: #94a3b8 !important;
  opacity: 0.8;
}

.dept-header-row {
  cursor: pointer;
}

.dept-header-row:hover {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
}

.dept-title-content {
  display: flex; 
  align-items: center; 
  gap: 8px;
}

.dept-title {
  font-weight: 700;
  color: #1e293b;
  font-size: 0.95rem;
}

.view-mode-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.edit-mode-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* Job Titles */
.jt-container {
  padding: 10px 10px 10px 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-left: 4px solid #334155;
  margin-left: 12px;
  background: #f8fafc;
}

.jt-block-nested {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}

.jt-main-row {
  padding: 10px 14px;
  cursor: pointer;
  background: #ffffff;
}

.jt-main-row:hover {
  background: #eff6ff;
}

.jt-title-content {
  display: flex; 
  align-items: center; 
  gap: 6px;
}

.jt-name {
  font-weight: 600;
  color: #334155;
  font-size: 0.88rem;
}

.jt-skill-preview {
  background: #eff6ff;
  padding: 12px 14px 12px 30px;
  border-top: 1px solid #bfdbfe;
  border-left: 4px solid #3b82f6;
  margin-left: 20px;
  border-radius: 0 0 8px 8px;
}

.jt-skill-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.jt-skill-item {
  background: #dbeafe;
  color: #1d4ed8;
  font-size: 0.72rem;
  padding: 4px 12px;
  border-radius: 100px;
  font-weight: 700;
  border: 1px solid #bfdbfe;
  box-shadow: 0 1px 2px rgba(37,99,235,0.1);
}

.jt-no-skill-hint {
  font-size: 0.75rem; 
  color: #93c5fd; 
  padding: 4px 10px;
  font-style: italic;
}

/* Skills Pool */
.skill-block-nested {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.04);
  margin-bottom: 8px;
}

.skill-main-row {
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
}

.clickable-row {
  cursor: pointer;
}

.clickable-row:hover {
  background: #f0fdf4;
}


.skill-details-area {
  padding: 16px 16px 16px 32px;
  background: #f0fdf4;
  border-top: 1px solid #bbf7d0;
  border-left: 4px solid #22c55e;
  margin-left: 16px;
  border-radius: 0 0 8px 8px;
}

.skill-details-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-label {
  display: block;
  font-size: 0.7rem;
  font-weight: 800;
  color: #94a3b8;
  text-transform: uppercase;
  margin-bottom: 6px;
  letter-spacing: 0.05em;
}

.skill-desc-text {
  font-size: 0.88rem;
  color: #475569;
  line-height: 1.5;
  margin: 0;
}

.sub-skills-mini-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.sub-skill-pill {
  font-size: 0.72rem;
  background: white;
  color: #1e293b;
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  font-weight: 600;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}

.no-sub-hint {
  font-size: 0.75rem;
  color: #cbd5e1;
  font-style: italic;
}

.skill-footer-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 12px;
  border-top: 1px dashed #f1f5f9;
}

.btn-edit-skill {
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit-skill:hover {
  background: #dbeafe;
  border-color: #3b82f6;
  transform: translateY(-1px);
}

/* Buttons */
.btn-primary {
  background: #1a2a3a;
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary-xs {
  background: #1a2a3a;
  color: white;
  border: none;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
}

.btn-cancel-xs {
  background: #cbd5e1;
  color: #1e293b;
  border: none;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
}

.btn-ghost-add {
  background: transparent;
  border: 1px dashed #cbd5e1;
  color: #64748b;
  padding: 8px;
  border-radius: 8px;
  width: 100%;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.btn-ghost-add:hover {
  background: white;
  border-color: #3b82f6;
  color: #3b82f6;
}

.btn-action-pill {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  color: #475569;
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 100px;
  cursor: pointer;
  font-weight: 600;
}

.btn-action-pill:hover {
  background: #e2e8f0;
}

.action-icon-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.action-icon-btn:hover {
  opacity: 1;
}

/* Icons */
.drag-handle, .drag-handle-jt {
  cursor: grab;
  color: #cbd5e1;
  font-family: serif;
  font-weight: bold;
}

.toggle-icon, .toggle-icon-sm {
  font-size: 0.7rem;
  color: #94a3b8;
  width: 14px;
  display: inline-block;
  text-align: center;
}

/* Modals */

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
  padding: 20px;
}

.modal-box {
  background: white;
  border-radius: 16px;
  padding: 32px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-title {
  margin-top: 0;
  font-size: 1.25rem;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 0.82rem;
  font-weight: 700;
  color: #64748b;
  margin-bottom: 8px;
}

.form-label-checklist {
  display: block;
  font-size: 0.75rem; 
  font-weight: 800; 
  color: #475569; 
  text-transform: uppercase;
  margin-bottom: 12px;
  letter-spacing: 0.025em;
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.95rem;
  color: #1e293b;
  transition: all 0.2s;
  background: #f8fafc;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.sub-skills-section {
  background: #f1f5f9;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 24px;
}

.add-sub-skill-form {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  margin-bottom: 16px;
}

.add-sub-inputs {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.add-sub-skill-form .form-input {
  width: 100%;
  background: white;
}

.form-input-sm {
  font-size: 0.82rem !important;
  padding: 8px 12px !important;
}

.btn-add-sub {
  flex-shrink: 0;
  height: 40px;
  padding: 0 20px !important;
  white-space: nowrap;
}

.sub-skills-list-admin {
  max-height: 220px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-right: 4px;
}

.sub-skill-admin-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s;
  gap: 12px;
}

.sub-skill-admin-item:hover {
  border-color: #cbd5e1;
  box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}

.sub-skill-name-text {
  font-size: 0.9rem;
  color: #334155;
  font-weight: 500;
  flex: 1;
  line-height: 1.4;
}

.sub-skill-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.btn-action-sm {
  width: 32px;
  height: 32px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  text-decoration: none;
  color: #64748b;
}

.btn-action-sm.btn-video:hover {
  background: #dbeafe;
  border-color: #93c5fd;
  color: #2563eb;
  transform: scale(1.05);
}

.btn-action-sm.btn-edit-link:hover {
  background: #fef3c7;
  border-color: #fcd34d;
  color: #d97706;
  transform: scale(1.05);
}

.btn-action-sm.btn-trash:hover {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #dc2626;
  transform: scale(1.05);
}

.sub-skill-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.video-status-badge {
  display: inline-block;
  font-size: 0.65rem;
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 700;
  width: fit-content;
}

.video-status-badge.has-video {
  background: #dcfce7;
  color: #166534;
}

.video-status-badge.no-video {
  background: #f1f5f9;
  color: #64748b;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 25px;
}

.scrollable-list {
  max-height: 400px; 
  overflow-y: auto;
}

.skill-assign-item {
  cursor: pointer; 
  display: flex; 
  align-items: center; 
  gap: 10px;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background 0.2s;
}

.skill-assign-item:hover {
  background: #f1f5f9;
}

.assign-checkbox {
  width: 18px; 
  height: 18px;
  cursor: pointer;
}

.btn-cancel {
  background: #f1f5f9;
  color: #475569;
  border: none;
  padding: 10px 22px;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #e2e8f0;
}

/* Misc */
.drag-handle, .drag-handle-jt {
  cursor: grab;
  color: #94a3b8;
  padding: 4px 8px;
  margin-right: 8px;
  font-size: 1.2rem;
  user-select: none;
  transition: color 0.2s;
}

.drag-handle:hover, .drag-handle-jt:hover {
  color: #64748b;
}

.drag-handle:active, .drag-handle-jt:active {
  cursor: grabbing;
}

.drag-ghost {
  opacity: 0.4;
  background: #e0f2fe !important;
}

.no-data-hint-sm {
  font-size: 0.8rem;
  color: #94a3b8;
  text-align: center;
  padding: 20px;
}

.uncat-skill-row, .cat-header-row {
  cursor: pointer;
}

@media (max-width: 1024px) {
  .hr-settings-grid {
    grid-template-columns: 1fr;
  }
}

/* ─── Video Player Modal Styles ─── */
.video-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  z-index: 999999;
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
</style>

<style>
/* Global: Force SweetAlert above modals */
.swal2-container {
  z-index: 99999 !important;
}

/* ─── Sub-skill Dropdown List ─── */
.sub-skills-dropdown-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 8px;
}

.sub-skill-dropdown-item {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  background: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.sub-skill-dropdown-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
  user-select: none;
  transition: background 0.15s;
}

.sub-skill-dropdown-header:hover {
  background: #f8fafc;
}

.sub-dd-toggle {
  font-size: 0.8rem;
  color: #94a3b8;
  width: 14px;
  flex-shrink: 0;
}

.sub-dd-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #334155;
  flex: 1;
}

.sub-dd-video-dot {
  font-size: 0.9rem;
  flex-shrink: 0;
}

.sub-skill-dropdown-body {
  padding: 12px 16px 12px 40px;
  background: #f1f5f9;
  border-top: 1px solid #e2e8f0;
}

.sub-dd-video-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sub-dd-label {
  font-size: 0.8rem;
  color: #64748b;
  font-weight: 700;
}

.sub-dd-play-btn {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(37,99,235,0.2);
}

.sub-dd-play-btn:hover {
  background: linear-gradient(135deg, #1d4ed8, #2563eb);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(37,99,235,0.4);
}

.sub-dd-no-video {
  font-size: 0.8rem;
  color: #94a3b8;
  font-style: italic;
}

/* Drag & Drop Handles */
.drag-handle-skill {
  cursor: grab !important;
  color: #94a3b8;
  margin-right: 8px;
  font-weight: bold;
  font-size: 1.1rem;
  user-select: none;
  display: inline-block;
  padding: 0 4px;
}
.drag-handle-skill:hover {
  color: #2563eb;
}
.drag-handle-sub {
  cursor: grab !important;
  color: #94a3b8;
  margin-right: 10px;
  font-weight: bold;
  font-size: 1rem;
  user-select: none;
  display: inline-block;
  padding: 0 4px;
}
.drag-handle-sub:hover {
  color: #2563eb;
}
.drag-ghost {
  opacity: 0.4;
  background: #f1f5f9 !important;
  border: 1px dashed #2563eb !important;
}
</style>
