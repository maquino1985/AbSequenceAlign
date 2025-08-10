// Polyfills for Node.js modules in browser environment
import { Buffer } from 'buffer'
import crypto from 'crypto-browserify'

// Make crypto available globally
if (typeof window !== 'undefined') {
  (window as Record<string, unknown>).crypto = crypto
  ;(window as Record<string, unknown>).Buffer = Buffer
}

// Export for use in other files
export { crypto, Buffer }
