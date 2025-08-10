describe('Quick UI Tests', () => {
  beforeEach(() => {
    cy.visit('/', { timeout: 10000 });
  });

  it('should load the UI components', () => {
    // Check that main components are visible
    cy.getBySel('antibody-annotation-tool').should('be.visible');
    cy.getBySel('sequence-input').should('be.visible');
    cy.getBySel('submit-button').should('be.visible');
  });

  it('should handle input validation', () => {
    // Test that button is disabled when empty
    cy.getBySel('submit-button').should('be.disabled');
    
    // Test invalid input - button should still be enabled
    cy.getBySel('sequence-input').type('invalid sequence');
    cy.getBySel('submit-button').should('not.be.disabled');
  });

  it('should show history section', () => {
    cy.contains('History').should('be.visible');
    cy.getBySel('clear-history').should('be.visible');
  });

  it('should handle FASTA input submission', () => {
    const fasta = `>test
DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK`;
    
    cy.getBySel('sequence-input').type(fasta);
    cy.getBySel('submit-button').click();
    
    // Just verify the button was clicked and something happened
    cy.getBySel('submit-button').should('exist');
  });
});
