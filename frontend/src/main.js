/**
 * ไฟล์: frontend/src/main.js
 * หน้าที่: จุดเริ่มต้นของโปรแกรม Vue (Entry Point)
 * รายละเอียด:
 * - เป็นไฟล์แรกที่จะถูกเรียกทำงานเมื่อเปิดเว็บ
 * - ทำหน้าที่สร้างแอปพลิเคชันหลัก (Vue App)
 * - โหลด App.vue เข้าไปแปะในหน้าเว็บ (mount) ที่ <div id="app">
 */
import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
