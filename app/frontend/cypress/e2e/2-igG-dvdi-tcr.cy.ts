describe('IgG / DVD-Ig / TCR Annotation', () => {
  beforeEach(() => {
    cy.visit('/', { timeout: 10000 });
  });

  it('should annotate IgG with constant regions', () => {
    const igg = `>Humira_Heavy
EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSSASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSSLGTQTYICNVNHKPSNTKVDKKVEPKSCDKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK`;

    cy.getBySel('sequence-input').clear().type(igg, { delay: 0 });
    cy.getBySel('submit-button').click();
    
    // Wait for processing to complete
    cy.wait(3000);
    
    cy.getBySel('feature-table', { timeout: 15000 }).should('be.visible');
    cy.contains('CONSTANT').should('exist');
  });

  it('should annotate DVD-Ig with multiple variable domains', () => {
    const dvdi = `>scFv_DVDIg
DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIKGGGGGSGGGGSGGGGSGGGGSQVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS`;

    cy.getBySel('sequence-input').clear().type(dvdi, { delay: 0 });
    cy.getBySel('submit-button').click();
    
    // Wait for processing to complete
    cy.wait(3000);
    
    cy.getBySel('feature-table', { timeout: 15000 }).should('be.visible');
    cy.contains('LINKER').should('exist');
  });

  it('should annotate TCR sequence', () => {
    const tcr = `>TCR
AVDPVTGGSFNLTCSVSGDIQGDQVTQCLRINSESGVHWVKQAPGQGLQWIGLIDPYGGGTYNQKFKDKATLTVDKSSSTAYMELSSLTSEDSAVYFCASSQDRGNSGELFGGGTRLTVT`;

    cy.getBySel('sequence-input').clear().type(tcr, { delay: 0 });
    cy.getBySel('submit-button').click();
    
    // Wait for processing to complete
    cy.wait(3000);
    
    cy.getBySel('feature-table', { timeout: 15000 }).should('be.visible');
  });

  it('should handle history functionality', () => {
    const seq = `>hist_test
DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK`;

    cy.getBySel('sequence-input').clear().type(seq, { delay: 0 });
    cy.getBySel('submit-button').click();
    
    // Wait for processing to complete
    cy.wait(3000);
    
    cy.getBySel('feature-table', { timeout: 15000 }).should('be.visible');
    
    // Test history reload
    cy.get('[data-testid^="history-reload-"]').first().click();
    cy.getBySel('feature-table').should('be.visible');
    
    // Test history re-annotate
    cy.get('[data-testid^="history-reannotate-"]').first().click();
    cy.getBySel('feature-table', { timeout: 15000 }).should('be.visible');
    
    // Test clear history
    cy.getBySel('clear-history').click();
  });
});


