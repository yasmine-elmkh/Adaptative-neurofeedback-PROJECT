import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        ws: true,
        configure: (proxy) => {
          proxy.on('error', () => {})
          proxy.on('proxyReqWs', (_, __, socket) => { socket.on('error', () => {}) })
          proxy.on('proxyResWs', (_, __, socket) => { socket.on('error', () => {}) })
        },
      },
      '/ws': {
        target: 'ws://localhost:8001',
        ws: true,
        configure: (proxy) => {
          proxy.on('error', () => {})
          proxy.on('proxyReqWs', (_, __, socket) => { socket.on('error', () => {}) })
          proxy.on('proxyResWs', (_, __, socket) => { socket.on('error', () => {}) })
        },
      },
    },
  },
})