import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // tunnel orqali kirish uchun
    allowedHosts: true,
  },
})
