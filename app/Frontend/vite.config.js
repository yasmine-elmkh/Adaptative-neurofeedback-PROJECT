import { defineConfig, createLogger } from 'vite'
import react from '@vitejs/plugin-react'

const silenceWsProxy = (proxy) => {
  proxy.on('error', () => {})
  proxy.on('open',        (socket)        => { socket.on('error', () => {}) })
  proxy.on('proxyReqWs', (_, __, socket) => { socket.on('error', () => {}) })
  proxy.on('proxyResWs', (_, __, socket) => { socket.on('error', () => {}) })
}

const logger = createLogger()
const _origError = logger.error.bind(logger)
logger.error = (msg, opts) => {
  if (msg.includes('ECONNABORTED') || msg.includes('ECONNRESET')) return
  _origError(msg, opts)
}

export default defineConfig({
  customLogger: logger,
  plugins: [
    react(),
    // Silence ECONNABORTED on the raw upgrade socket (browser tab closed mid-write)
    {
      name: 'silence-ws-econnaborted',
      configureServer(server) {
        server.httpServer?.on('upgrade', (_req, socket) => {
          socket.on('error', () => {})
        })
      },
    },
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://localhost:8001', changeOrigin: true, ws: true, configure: silenceWsProxy },
      '/ws':  { target: 'ws://localhost:8001',   ws: true,           configure: silenceWsProxy },
    },
  },
})
