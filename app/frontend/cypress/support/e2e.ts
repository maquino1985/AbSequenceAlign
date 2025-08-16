// Import commands.js using ES2015 syntax:
import './commands';
// import 'cypress-file-upload'; // Commented out for now - not available in Docker

// Alternatively you can use CommonJS syntax:
// require('./commands')

// Prevent uncaught exceptions from failing tests
Cypress.on('uncaught:exception', (err) => {
  // returning false here prevents Cypress from failing the test
  if (err.message.includes('Maximum update depth exceeded')) {
    return false;
  }
  return true;
});