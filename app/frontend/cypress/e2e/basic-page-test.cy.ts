describe('Basic Page Test', () => {
  it('should load the page', () => {
    cy.visit('/')
    
    // Wait for page to load
    cy.wait(5000)
    
    // Check that the page has loaded
    cy.get('body').should('exist')
    
    // Check that the root div exists
    cy.get('#root').should('exist')
    
    // Log the page title
    cy.title().then((title) => {
      cy.log('Page title:', title)
    })
    
    // Log the page content
    cy.get('body').then(($body) => {
      cy.log('Body text (first 200 chars):', $body.text().substring(0, 200))
    })
    
    // Take a screenshot
    cy.screenshot('basic-page-test')
  })
})
