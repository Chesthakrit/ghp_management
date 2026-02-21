import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',  // ← ให้มือถือในวง LAN เดียวกันเข้าถึงได้
    port: 5173,
  }
})
