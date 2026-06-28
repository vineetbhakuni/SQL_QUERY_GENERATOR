import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': 'http://localhost:8001',
      '/query': 'http://localhost:8001',
      '/history': 'http://localhost:8001',
      '/health': 'http://localhost:8001',
    },
  },
})
