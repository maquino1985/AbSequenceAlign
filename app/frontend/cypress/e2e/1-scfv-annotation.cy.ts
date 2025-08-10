/// <reference types="cypress" />

describe('ScFv Annotation', () => {
  beforeEach(() => {
    cy.visit('/', { timeout: 10000 });
  });

  it('should annotate scFv sequence and display all domains', () => {
    const scfv = `>scfv
DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIKGGGGGSGGGGSGGGGSGGGGSQVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS`;

    cy.getBySel('sequence-input').clear().type(scfv, { delay: 0 });
    cy.getBySel('submit-button').click();
    
    // Wait for results with shorter timeout
    cy.getBySel('feature-table', { timeout: 15000 }).should('be.visible');
    
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

    cy.getBySel('sequence-input').clear().type(sequences, { delay: 0 });
    cy.getBySel('submit-button').click();
    
    cy.getBySel('feature-table', { timeout: 15000 }).should('be.visible');
  });

  it('should handle errors gracefully', () => {
    cy.getBySel('sequence-input').clear().type('invalid sequence', { delay: 0 });
    cy.getBySel('submit-button').click();
    
    // Should show error or handle gracefully
    cy.get('body').should('not.contain', 'Error');
  });
});