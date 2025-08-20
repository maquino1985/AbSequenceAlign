describe('Simple BLAST Test', () => {
  it('should load the page and verify basic functionality', () => {
    cy.visit('/')
    
    // Wait for page to load
    cy.wait(3000)
    
    // Check that the page has loaded (look for any text that should be there)
    cy.get('body').should('contain', 'BLAST')
    
    // Check that we can see the form elements
    cy.get('form').should('exist')
    
    // Check that we can see a textarea (for sequence input)
    cy.get('textarea').should('exist')
    
    // Check that we can see buttons
    cy.get('button').should('exist')
    
    // Take a screenshot for verification
    cy.screenshot('simple-blast-test')
  })
})
