/// <reference types="cypress" />

describe('ScFv Annotation', () => {
  beforeEach(() => {
    cy.visit('/antibody-annotation', { timeout: 10000 });
    // Wait for the app to load
    cy.get('[data-testid="antibody-annotation-tool"]', { timeout: 10000 }).should('be.visible');
  });

  it('should annotate scFv sequence and display all domains', () => {
    const scfv = `>scfv
DIVLTQSPATLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIKGGGGGSGGGGSGGGGSGGGGSQVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS`;

    // Debug: Check if elements are visible
    cy.getBySel('sequence-input').should('be.visible').clear().type(scfv, { delay: 0 });
    cy.getBySel('submit-button').should('be.visible').click();
    
    // Debug: Check for loading state
    // cy.get('[data-testid="loading-indicator"]', { timeout: 5000 }).should('be.visible');
    
    // Debug: Wait for loading to complete
    // cy.get('[data-testid="loading-indicator"]', { timeout: 30000 }).should('not.exist');
    
    // Wait for results with shorter timeout
    cy.getBySel('feature-table', { timeout: 3000 }).should('be.visible');
    
    // Quick checks for key elements
    cy.contains('FR1').should('exist');
    cy.contains('CDR1').should('exist');
    cy.contains('LINKER').should('exist');
  });

  it('should handle multiple sequences', () => {
    const sequences = `>seq1
DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK
>seq2
QVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS`;

    cy.getBySel('sequence-input').should('be.visible').clear().type(sequences, { delay: 0 });
    cy.getBySel('submit-button').should('be.visible').click();
    
    
    cy.getBySel('feature-table', { timeout: 15000 }).should('be.visible');
  });

  it('should handle errors gracefully', () => {
    cy.getBySel('sequence-input').should('be.visible').clear().type('invalid sequence', { delay: 0 });
    cy.getBySel('submit-button').should('be.visible').click();
    
    // Should show error or handle gracefully
    cy.get('body').should('not.contain', 'Error');
  });
});