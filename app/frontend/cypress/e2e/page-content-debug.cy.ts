describe('Page Content Debug', () => {
  it('should show what content is actually on the page', () => {
    cy.visit('/')
    
    // Wait for page to load
    cy.wait(5000)
    
    // Log all text content
    cy.get('body').then(($body) => {
      const text = $body.text()
      cy.log('Full page text (first 1000 chars):', text.substring(0, 1000))
      
      // Log all headings
      cy.log('All h1 elements:', $body.find('h1').map((i, el) => el.textContent).get().join(', '))
      cy.log('All h2 elements:', $body.find('h2').map((i, el) => el.textContent).get().join(', '))
      cy.log('All h3 elements:', $body.find('h3').map((i, el) => el.textContent).get().join(', '))
      cy.log('All h4 elements:', $body.find('h4').map((i, el) => el.textContent).get().join(', '))
      cy.log('All h5 elements:', $body.find('h5').map((i, el) => el.textContent).get().join(', '))
      cy.log('All h6 elements:', $body.find('h6').map((i, el) => el.textContent).get().join(', '))
      
      // Log all labels
      cy.log('All label elements:', $body.find('label').map((i, el) => el.textContent).get().join(', '))
      
      // Log all buttons
      cy.log('All button elements:', $body.find('button').map((i, el) => el.textContent).get().join(', '))
    })
    
    // Take a screenshot
    cy.screenshot('page-content-debug')
  })
})
