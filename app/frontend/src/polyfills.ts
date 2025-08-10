// Polyfills for Node.js modules in browser environment
import { Buffer } from 'buffer'
import crypto from 'crypto-browserify'

// Make crypto available globally
if (typeof window !== 'undefined') {
  (window as any).crypto = crypto
  (window as any).Buffer = Buffer
}

// Export for use in other files
export { crypto, Buffer }
