# Project Context Summary: GHP ERP System (Attendance & OT Module)

## 📌 Project Overview
- **Name:** GHP Management (ERP Solution)
- **Target Device:** Highly optimized for **iPad (Tablet)** use in factory/office environments.
- **Goal:** To manage employee resources, specifically starting with a robust Attendance and Overtime (OT) system that is secure, accurate, and professional.

## 🛠 Technology Stack
- **Backend:** Python (FastAPI), SQLAlchemy (ORM), PostgreSQL/SQLite (Database), Pydantic (Schemas).
- **Frontend:** Vue 3, Vite, Vanilla CSS (Premium & Custom Design), FontAwesome, SweetAlert2.
- **Authentication:** JWT (OAuth2 Password Bearer).

## ✅ Current Progress (Implemented Features)
### 1. Attendance System
- **Check-in/Check-out:** Supports GPS coordinates, IP address tracking, and image uploads.
- **Lateness Calculation:** Server-side logic to determine lateness levels (T1, T2, T3) based on grace periods.
- **Settings:** Dynamic configuration panel for working hours (Check-in/Check-out) and grace periods.

### 2. Overtime (OT) System
- **Morning OT Support:** Implemented configuration and logic for pre-work overtime (e.g., 05:00 - 08:00).
- **Magic Button (Auto-fill):** User can auto-populate OT requests based on their actual clock-out time.
- **Calculation Engine:** Robust minute-based splitting between **Standard OT** and **Special OT** (Night/Holiday). This is implemented on both Frontend (for UX) and Backend (for Security).
- **Database Model:** `OTRequest` table created to store requests with `pending`, `approved`, or `rejected` statuses.

### 3. Security Hardening
- **Authorization:** Only authorized users (Admin/HR) or the account owner can view attendance/OT logs.
- **Data Integrity:** All time-sensitive calculations are re-validated on the server to prevent manual frontend manipulation.
- **Input Sanitation:** Prepared for cleaner input handling.

## 🗺 Future Roadmap (Next Steps)
1. **OT Approval Portal:** Create an admin interface to review, approve, or reject pending `OTRequest` records.
2. **Dashboard & Analytics:** Visual charts showing daily attendance, department-wise OT costs, and late trends.
3. **Payroll Integration:** Linking approved OT hours directly to salary calculation.
4. **Audit Trail:** Implementing logs to track who edited/approved any attendance records.

## ⚙️ Configuration Keys used in DB
- `check_in_time`, `check_out_time`
- `late_grace_period_mins`, `_t2`, `_t3`
- `ot_normal_start`, `ot_normal_end`
- `ot_special_start`, `ot_special_end`
- `ot_morning_start`, `ot_morning_end`

---
*This document serves as a bridge for the next development context.*

---

# สรุปข้อมูลโปรเจกต์: ระบบ ERP GHP (โมดูลบันทึกเวลาและ OT)

## 📌 ภาพรวมโปรเจกต์
- **ชื่อ:** GHP Management (โซลูชัน ERP สำหรับองค์กร)
- **อุปกรณ์เป้าหมาย:** ออกแบบมาให้ใช้งานได้ดีเยี่ยมบน **iPad (Tablet)** สำหรับการใช้งานในโรงงานหรือสำนักงาน
- **เป้าหมาย:** บริหารจัดการทรัพยากรบุคคล เริ่มต้นด้วยระบบบันทึกเวลาทำงาน (Attendance) และโอที (OT) ที่มีความปลอดภัย แม่นยำ และดูเป็นมืออาชีพ

## 🛠 เทคโนโลยีที่ใช้
- **หลังบ้าน (Backend):** Python (FastAPI), SQLAlchemy (ORM), SQL Database, Pydantic (Schemas)
- **หน้าบ้าน (Frontend):** Vue 3, Vite, Vanilla CSS (เน้นดีไซน์ระดับพรีเมียม), FontAwesome, SweetAlert2
- **การยืนยันตัวตน:** JWT (OAuth2 Password Bearer)

## ✅ ความคืบหน้าปัจจุบัน (ฟีเจอร์ที่ทำเสร็จแล้ว)
### 1. ระบบบันทึกเวลา (Attendance System)
- **การเข้า-ออกงาน:** รองรับการเก็บพิกัด GPS, ที่อยู่ IP, และการอัปโหลดรูปถ่าย
- **การคำนวณการสาย:** มีลอจิกฝั่ง Server เพื่อตัดสินระดับการสาย (T1, T2, T3) ตามช่วงเวลาผ่อนผันที่ตั้งค่าได้
- **การตั้งค่า:** มีหน้าจอตั้งค่าแบบ Dynamic สำหรับจัดการเวลาเข้า-ออกงาน และช่วงเวลาผ่อนผัน

### 2. ระบบโอที (Overtime System)
- **รองรับโอทีเช้า:** เพิ่มการตั้งค่าและลอจิกสำหรับโอทีช่วงก่อนเริ่มงาน (เช่น 05:00 - 08:00)
- **ปุ่มวิเศษ (Auto-fill):** พนักงานสามารถกดดึงเวลาเลิกงานจริงมาใส่ในคำขอ OT ได้ทันที
- **ระบบคำนวณชั่วโมง:** ระบบแยกชั่วโมงโอทีเป็น **Standard OT** และ **Special OT** (ภาคค่ำ/วันหยุด/เช้ามืด) อย่างแม่นยำ โดยมีการคำนวณทั้งฝั่งหน้าบ้าน (เพื่อ UX) และหลังบ้าน (เพื่อความปลอดภัย)
- **ฐานข้อมูล:** ใช้ตาราง `OTRequest` เก็บข้อมูลสถานะทั้ง `รออนุมัติ`, `อนุมัติแล้ว`, หรือ `ปฏิเสธ`

### 3. การเสริมความปลอดภัย (Security Hardening)
- **สิทธิ์การเข้าถึง:** จำกัดให้เฉพาะผู้ที่มีสิทธิ์ (Admin/HR) หรือเจ้าของข้อมูลเท่านั้นที่ดูประวัติได้
- **ความถูกต้องของข้อมูล:** ลอจิกการคำนวณเวลาที่สำคัญทั้งหมดจะถูกตรวจสอบซ้ำที่ Server เพื่อป้องกันพนักงานแก้ไขตัวเลขเองจากหน้าจอ

## 🗺 แผนการพัฒนาต่อ (Roadmap)
1. **ระบบอนุมัติ OT (Admin Portal):** สร้างหน้าจอสำหรับให้ Admin/HR ตรวจสอบและกดอนุมัติคำขอที่ค้างอยู่
2. **แดชบอร์ดและรายงาน:** กราฟแสดงสถิติการมาสาย ยอดจ่ายค่า OT รายแผนก และแนวโน้มรายเดือน
3. **เชื่อมต่อระบบเงินเดือน (Payroll):** นำชั่วโมง OT ที่อนุมัติแล้วไปคำนวณเป็นยอดเงินเดือนโดยตรง
4. **บันทึกประวัติการแก้ไข (Audit Trail):** ระบบบันทึกว่าใครเป็นคนอนุมัติหรือแก้ไขข้อมูลเวลา เพื่อความโปร่งใส

## ⚙️ คีย์การตั้งค่าในฐานข้อมูล
- `check_in_time`, `check_out_time` (เวลาเข้า-ออกงานปกติ)
- `late_grace_period_mins`, `_t2`, `_t3` (ช่วงเวลาผ่อนผัน)
- `ot_normal_start`, `ot_normal_end` (โอทีมาตรฐาน)
- `ot_special_start`, `ot_special_end` (โอทีพิเศษ/ดึก)
- `ot_morning_start`, `ot_morning_end` (โอทีช่วงเช้า)

---
*เอกสารนี้จัดทำขึ้นเพื่อใช้เป็นข้อมูลอ้างอิงสำหรับการพัฒนาในขั้นตอนต่อไป*
