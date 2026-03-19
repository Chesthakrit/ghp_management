<template>
  <div class="mgmt-wrapper">
    <!-- Header Section -->
    <div class="mgmt-header">
      <div class="header-main">
        <h1 class="mgmt-title"><i class="fas fa-edit mr-2"></i> Policy Management</h1>
        <p class="mgmt-subtitle">จัดการเนื้อหากฎระเบียบ สวัสดิการ และประกาศของบริษัท</p>
      </div>
      <div class="header-actions">
        <button class="btn-primary" @click="saveAll">
          <i class="fas fa-save"></i> Save All Changes
        </button>
      </div>
    </div>

    <!-- Management Dashboard Grid -->
    <div class="mgmt-grid">
      <!-- Card for each policy category -->
      <div v-for="cat in categories" :key="cat.id" class="mgmt-card">
        <div class="card-header" :class="cat.colorClass">
          <div class="header-icon">
            <i :class="cat.icon"></i>
          </div>
          <div class="header-info">
            <h3 class="card-title">{{ cat.title }}</h3>
            <span class="card-tag">ADMIN CONFIG</span>
          </div>
        </div>

        <div class="card-body">
          <div class="form-group">
            <label class="form-label">คำอธิบายห้วข้อ (Description)</label>
            <input v-model="cat.desc" class="form-input" placeholder="สรุปเนื้อหาเบื้องต้น..." />
          </div>
          <div class="form-group mt-16">
            <label class="form-label">เนื้อหาหลัก (Main Content)</label>
            <textarea v-model="cat.content" class="form-textarea" placeholder="ระบุรายละเอียดเป็นหัวข้อ หรือข้อความที่ต้องการสื่อสาร..." rows="6"></textarea>
          </div>
        </div>

        <div class="card-footer">
          <div class="status-badge" :class="{ 'is-saved': !cat.dirty }">
             <i :class="cat.dirty ? 'fas fa-pen-nib' : 'fas fa-check-circle'"></i> 
             {{ cat.dirty ? 'Edited' : 'Published' }}
          </div>
          <button class="btn-view-preview" title="ดูภาพตัวย่างฝั่งพนักงาน">
            Preview <i class="fas fa-external-link-alt"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import Swal from 'sweetalert2'

const categories = ref([
  { id: 'rules', title: 'กฎระเบียบบริษัท', icon: 'fas fa-gavel', desc: 'ข้อบังคับเกี่ยวกับการทำงาน เวลาเข้า-ออกงาน และระเบียบวินัยทั่วไป', content: '', colorClass: 'bg-blue', dirty: false },
  { id: 'welfare', title: 'สวัสดิการ', icon: 'fas fa-hand-holding-heart', desc: 'ข้อมูลประกันสังคม ประกันกลุ่ม โบนัส และสวัสดิการพนักงานอื่นๆ', content: '', colorClass: 'bg-green', dirty: false },
  { id: 'holidays', title: 'วันหยุด & วันลา', icon: 'fas fa-calendar-alt', desc: 'ปฏิทินวันหยุดประจำปี โควตาวันลาพักร้อน ลาป่วย และการขออนุมัติ', content: '', colorClass: 'bg-amber', dirty: false },
  { id: 'penalty', title: 'การลงโทษ & วินัย', icon: 'fas fa-exclamation-triangle', desc: 'ขั้นตอนการตักเตือน ระเบียบการลงโทษทางวินัยหากกระทำผิดข้อบังคับ', content: '', colorClass: 'bg-red', dirty: false },
  { id: 'others', title: 'ข้อมูลอื่นๆ', icon: 'fas fa-info-circle', desc: 'คู่มือพนักงาน แผงผังองค์กร และประกาศสำคัญจากบริษัท', content: '', colorClass: 'bg-purple', dirty: false }
])

// Watch for changes to mark them as "dirty"
categories.value.forEach(cat => {
  watch(() => [cat.desc, cat.content], () => {
    cat.dirty = true
  }, { deep: true })
})

const saveAll = async () => {
  // Logic การบันทึกลง Backend จะใส่ที่นี่
  try {
    // mock delay
    await new Promise(r => setTimeout(r, 1000))
    categories.value.forEach(cat => cat.dirty = false)
    Swal.fire({
      title: 'Success!',
      text: 'ทุกการตั้งค่าถูกบันทึกและอัปเดตไปแสดงที่หน้าพนักงานเรียบร้อยแล้ว',
      icon: 'success',
      confirmButtonText: 'รับทราบ',
      confirmButtonColor: '#3b82f6'
    })
  } catch (e) {
    Swal.fire('Error', 'ไม่สามารถบันทึกได้ กรุณาลองใหม่อีกครั้ง', 'error')
  }
}
</script>

<style scoped>
.mgmt-wrapper {
  animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.mgmt-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  background: white;
  padding: 24px 32px;
  border-radius: 20px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
  border: 1px solid #e2e8f0;
}

.mgmt-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #1e293b;
  margin: 0 0 6px 0;
}

.mgmt-subtitle {
  color: #64748b;
  margin: 0;
  font-size: 0.95rem;
}

.mgmt-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 28px;
}

.mgmt-card {
  background: white;
  border-radius: 24px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  transition: all 0.3s;
}

.mgmt-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 15px 35px rgba(0,0,0,0.08);
  border-color: #cbd5e1;
}

.card-header {
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid #f1f5f9;
}

.bg-blue { background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); color: #3b82f6; }
.bg-green { background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); color: #22c55e; }
.bg-amber { background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); color: #f59e0b; }
.bg-red { background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); color: #ef4444; }
.bg-purple { background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%); color: #a855f7; }

.header-icon {
  width: 54px;
  height: 54px;
  background: white;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

.card-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: #1e293b;
}

.card-tag {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.8;
}

.card-body {
  padding: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.95rem;
  color: #1e293b;
  background: #f8fafc;
  transition: all 0.2s;
}

.form-textarea {
  width: 100%;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  font-size: 0.95rem;
  color: #1e293b;
  background: #f8fafc;
  resize: vertical;
  transition: all 0.2s;
}

.form-input:focus, .form-textarea:focus {
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  outline: none;
}

.card-footer {
  padding: 16px 24px;
  background: #f8fafc;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f1f5f9;
}

.status-badge {
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  background: #fff;
  border: 1px solid #e2e8f0;
  color: #94a3b8;
}

.status-badge.is-saved {
  color: #22c55e;
  border-color: #dcfce7;
  background: #f0fdf4;
}

.btn-view-preview {
  background: transparent;
  border: none;
  color: #3b82f6;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-view-preview:hover {
  text-decoration: underline;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  padding: 12px 24px;
  border-radius: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 25px -5px rgba(37, 99, 235, 0.4);
}

.mt-16 { margin-top: 16px; }
.mr-2 { margin-right: 8px; }

@media (max-width: 768px) {
  .mgmt-grid { grid-template-columns: 1fr; }
}
</style>
