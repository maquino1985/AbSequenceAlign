/// <reference types="cypress" />

describe('ScFv Annotation', () => {
  beforeEach(() => {
    cy.visit('/', { timeout: 10000 });
  });

  it('should make API call and process response', () => {
    const scfv = `>scfv
DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK`;

    // Intercept the API call to see what's happening
    cy.intercept('POST', '**/api/v2/annotate', (req) => {
      req.alias = 'annotationRequest';
    }).as('annotationRequest');

    // Listen for console errors
    cy.window().then((win) => {
      cy.spy(win.console, 'error').as('consoleError');
      cy.spy(win.console, 'log').as('consoleLog');
    });

    cy.getBySel('sequence-input').clear().type(scfv, { delay: 0 });
    cy.getBySel('submit-button').click();
    
    // Wait for the API call to complete
    cy.wait('@annotationRequest', { timeout: 30000 }).then((interception) => {
      cy.log('API Response Status:', interception.response?.statusCode);
      cy.log('API Response Body:', JSON.stringify(interception.response?.body, null, 2));
    });
    
    // Check for console errors
    cy.get('@consoleError').should('not.have.been.called');
    
    // Wait a bit for the UI to update
    cy.wait(2000);
    
    // Check if any sequences are loaded
    cy.get('body').should('contain', 'scfv');
  });

  it('should handle multiple sequences', () => {
    const sequences = `>seq1
DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK
>seq2
QVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS`;

    cy.getBySel('sequence-input').clear().type(sequences, { delay: 0 });
    cy.getBySel('submit-button').click();
    
    // Wait for processing to complete
    cy.wait(3000);
    
    cy.getBySel('feature-table', { timeout: 15000 }).should('be.visible');
  });

  it('should handle errors gracefully', () => {
    cy.getBySel('sequence-input').clear().type('invalid sequence', { delay: 0 });
    cy.getBySel('submit-button').click();
    
    // Should show error or handle gracefully
    cy.get('body').should('not.contain', 'Error');
  });
});