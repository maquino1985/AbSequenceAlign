// Polyfills for Node.js modules in browser environment
import { Buffer } from 'buffer'
// eslint-disable-next-line @typescript-eslint/no-var-requires
const crypto = require('crypto-browserify')

// Make crypto available globally
if (typeof window !== 'undefined') {
  ;(window as unknown as Record<string, unknown>).crypto = crypto
  ;(window as unknown as Record<string, unknown>).Buffer = Buffer
}

// Export for use in other files
export { crypto, Buffer }
