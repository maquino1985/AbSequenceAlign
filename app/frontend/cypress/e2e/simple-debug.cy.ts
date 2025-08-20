describe('Simple Debug Test', () => {
  it('should load the page and show what content is available', () => {
    cy.visit('/')
    
    // Wait for page to load
    cy.wait(3000)
    
    // Log the page content for debugging
    cy.get('body').then(($body) => {
      cy.log('Page title:', $body.find('title').text())
      cy.log('All h1 elements:', $body.find('h1').map((i, el) => el.textContent).get().join(', '))
      cy.log('All h4 elements:', $body.find('h4').map((i, el) => el.textContent).get().join(', '))
      cy.log('All h6 elements:', $body.find('h6').map((i, el) => el.textContent).get().join(', '))
      cy.log('All text content:', $body.text().substring(0, 500))
    })
    
    // Check if there are any error messages (optional)
    cy.get('body').then(($body) => {
      const alerts = $body.find('[role="alert"]')
      if (alerts.length > 0) {
        cy.log('Error alerts found:', alerts.map((i, el) => el.textContent).get().join(', '))
      } else {
        cy.log('No error alerts found')
      }
    })
    
    // Take a screenshot for debugging
    cy.screenshot('debug-page-content')
  })
})
