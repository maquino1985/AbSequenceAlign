const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: process.env.CYPRESS_BASE_URL || 'http://localhost:5679',
    supportFile: 'cypress/support/e2e.ts',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: false,
    experimentalStudio: false,
    defaultCommandTimeout: 5000,
    requestTimeout: 8000,
    responseTimeout: 8000,
    pageLoadTimeout: 10000,
    // Fail fast settings
    stopOnSpecFailure: true,    // Stop running any more specs after a spec failure
    experimentalAbortOnSpecError: true, // Abort all tests if a spec fails
    retries: {
      runMode: 0,      // Don't retry in run mode
      openMode: 0      // Don't retry in open mode
    }
  },
  component: {
    devServer: {
      framework: 'react',
      bundler: 'vite',
    },
  },
  env: {
    backendPort: process.env.CYPRESS_BACKEND_PORT || 8000
  }
});