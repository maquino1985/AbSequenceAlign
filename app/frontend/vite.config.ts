/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
  // Fix for crypto.hash issue in CI environment
  define: {
    global: 'globalThis',
  },
  optimizeDeps: {
    include: ['react', 'react-dom'],
  },
  server: {
    // Ensure proper host binding for CI
    host: '0.0.0.0',
    port: parseInt(process.env.VITE_PORT || '3000'),
    strictPort: true,
  },
  // Fix for Node.js crypto polyfill in browser environment
  resolve: {
    alias: {
      crypto: 'crypto-browserify',
    },
  },
})