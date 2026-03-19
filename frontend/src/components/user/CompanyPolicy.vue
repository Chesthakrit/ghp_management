<template>
  <div class="policy-wrapper">
    <!-- Header Section -->
    <div class="policy-header-card">
      <div class="header-icon-box">
        <i class="fas fa-file-contract"></i>
      </div>
      <div class="header-text-info">
        <h1 class="policy-main-title">Company Policy & Welfare</h1>
        <p class="policy-sub-title">กฎระเบียบบริษัท สวัสดิการ และข้อมูลสวัสดิการพนักงาน</p>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="policy-grid">
      <!-- Section 1: กฎระเบียบบริษัท -->
      <div class="policy-section-card">
        <div class="section-icon color-blue">
          <i class="fas fa-gavel"></i>
        </div>
        <h3 class="section-title">กฎระเบียบบริษัท</h3>
        <p class="section-desc">ข้อบังคับเกี่ยวกับการทำงาน เวลาเข้า-ออกงาน และระเบียบวินัยทั่วไป</p>
        <button class="btn-policy-link">ดูรายละเอียด <i class="fas fa-arrow-right"></i></button>
      </div>

      <!-- Section 2: สวัสดิการ -->
      <div class="policy-section-card">
        <div class="section-icon color-green">
          <i class="fas fa-hand-holding-heart"></i>
        </div>
        <h3 class="section-title">สวัสดิการ</h3>
        <p class="section-desc">ข้อมูลประกันสังคม ประกันกลุ่ม โบนัส และสวัสดิการพนักงานอื่นๆ</p>
        <button class="btn-policy-link">ดูรายละเอียด <i class="fas fa-arrow-right"></i></button>
      </div>

      <!-- Section 3: วันหยุด & วันลา -->
      <div class="policy-section-card">
        <div class="section-icon color-amber">
          <i class="fas fa-calendar-alt"></i>
        </div>
        <h3 class="section-title">วันหยุด & วันลา</h3>
        <p class="section-desc">ปฏิทินวันหยุดประจำปี โควตาวันลาพักร้อน ลาป่วย และการขออนุมัติ</p>
        <button class="btn-policy-link">ดูรายละเอียด <i class="fas fa-arrow-right"></i></button>
      </div>

      <!-- Section 4: การลงโทษ & วินัย -->
      <div class="policy-section-card">
        <div class="section-icon color-red">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <h3 class="section-title">การลงโทษ & วินัย</h3>
        <p class="section-desc">ขั้นตอนการตักเตือน ระเบียบการลงโทษทางวินัยหากกระทำผิดข้อบังคับ</p>
        <button class="btn-policy-link">ดูรายละเอียด <i class="fas fa-arrow-right"></i></button>
      </div>

      <!-- Section 5: อื่นๆ -->
      <div class="policy-section-card">
        <div class="section-icon color-purple">
          <i class="fas fa-info-circle"></i>
        </div>
        <h3 class="section-title">ข้อมูลอื่นๆ</h3>
        <p class="section-desc">คู่มือพนักงาน แผงผังองค์กร และประกาศสำคัญจากบริษัท</p>
        <button class="btn-policy-link">ดูรายละเอียด <i class="fas fa-arrow-right"></i></button>
      </div>
    </div>

    <!-- Empty State / Coming Soon Placeholder -->
    <div class="coming-soon-banner">
      <i class="fas fa-tools"></i>
      <p>Content for each section is being updated. Please check back later.</p>
    </div>
  </div>
</template>

<script setup>
// จะเพิ่ม Logic การดึงข้อมูลจาก DB ในอนาคตได้ที่นี่
</script>

<style scoped>
.policy-wrapper {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.policy-header-card {
  background: white;
  padding: 32px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 32px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  border: 1px solid #e2e8f0;
}

.header-icon-box {
  width: 64px;
  height: 64px;
  background: #eff6ff;
  color: #3b82f6;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
}

.policy-main-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.policy-sub-title {
  color: #64748b;
  margin: 0;
  font-size: 0.95rem;
}

.policy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.policy-section-card {
  background: white;
  padding: 24px;
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.policy-section-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 20px rgba(0,0,0,0.06);
  border-color: #cbd5e1;
}

.section-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  margin-bottom: 20px;
}

.color-blue { background: #eff6ff; color: #3b82f6; }
.color-green { background: #f0fdf4; color: #22c55e; }
.color-amber { background: #fffbeb; color: #f59e0b; }
.color-red { background: #fef2f2; color: #ef4444; }
.color-purple { background: #faf5ff; color: #a855f7; }

.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 12px 0;
}

.section-desc {
  font-size: 0.9rem;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 20px 0;
  flex: 1;
}

.btn-policy-link {
  background: transparent;
  border: none;
  color: #3b82f6;
  font-weight: 600;
  font-size: 0.85rem;
  padding: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: gap 0.2s;
}

.btn-policy-link:hover {
  gap: 12px;
  color: #2563eb;
}

.coming-soon-banner {
  background: #f8fafc;
  border: 2px dashed #e2e8f0;
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  color: #94a3b8;
}

.coming-soon-banner i {
  font-size: 2.5rem;
  margin-bottom: 16px;
  opacity: 0.5;
}

.coming-soon-banner p {
  margin: 0;
  font-weight: 500;
}
</style>
