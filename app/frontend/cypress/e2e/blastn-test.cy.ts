describe('BLASTN Search Test', () => {
  it('should perform BLASTN search with euk_cdna database', () => {
    cy.visit('/');
    
    // Wait for the page to load
    cy.get('#root', { timeout: 10000 }).should('exist');
    
    // Wait for the BLAST form to be visible
    cy.contains('BLAST Search Configuration', { timeout: 10000 }).should('be.visible');
    
    // Select BLASTN
    cy.get('label').contains('BLAST Type').parent().find('div[role="combobox"]').click();
    cy.get('li').contains('BLASTN').click();
    
    // Wait for BLASTN-specific parameters to appear
    cy.get('label').contains('Word Size', { timeout: 5000 }).should('be.visible');
    cy.get('label').contains('Percent Identity').should('be.visible');
    
    // Select euk_cdna database
    cy.get('label').contains('Database').parent().find('div[role="combobox"]').click();
    cy.get('li').contains('euk_cdna').click();
    
    // Enter test sequence
    const testSequence = 'GAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGCGGCTTTACTTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAATGGGTGAGCGCGATTACCTGGAACAGCGGCCATATTGATTATGCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTATCTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGCGCGAAAGTGAGCTATCTGAGCACCGCGAGCAGCCTGGATTATTGGGGCCAGGGCACCCTGGTGACCGTGAGCAGCGCGAGCACCAAAGGCCCGAGCGTGTTTCCGCTGGCGCCGAGCAGCAAAAGCACCAGCGGCGGCACCGCGGCGCTGGGCTGCCTGGTGAAAGATTATTTTCCGGAACCGGTGACCGTGAGCTGGAACAGCGGCGCGCTGACCAGCGGCGTGCATACCTTTCCGGCGGTGCTGCAGAGCAGCGGCCTGTATAGCCTGAGCAGCGTGGTGACCGTGCCGAGCAGCAGCCTGGGCACCCAGACCTATATTTGCAACGTGAACCATAAACCGAGCAACACCAAAGTGGATAAAAAAGTGGAAACCGAAAAGCTGCGATAAAACCCATACCTGCCCGCCGTGCCCGGGCCCGGAACTGCTGGGCGGCCCGAGCGTGTTTCTGTTTCCGCCGAAACCGAAAGATACCCTGATGATTAGCCGCACCCCGGAAGTGACCTGCGTGGTGGTGGATGTGAGCCATGAAGATCCGGAAGTGAAATTTAACTGGTATGTGGATGGCGTGGAAGTGCATAACGCGAAAACCAAACCGCGCGAAGAACAGTATAACAGCACCTATCGCGTGGTGAGCGTGCTGACCGTGCTGGATAGCGATGGCAGCTTTTTTCTGTATAGCAAACTGACCGTGGATAAAAGCCGCTGGCAGCAGGGCAACGTGTTTAGCTGCAGCGTGATGCATGAAGCGCTGCATAACCATTATACCCAGAAAAGCCTGAGCCTGAGCCCGGGCAAA';
    
    cy.get('textarea').clear().type(testSequence);
    
    // Click search button
    cy.contains('Run BLAST Search').click();
    
    // Wait for results (this may take a while)
    cy.contains('Search Results', { timeout: 30000 }).should('be.visible');
    
    // Check that we have results
    cy.get('[data-testid="blast-results"]', { timeout: 5000 }).should('exist');
    
    // Verify we have hits
    cy.contains('ENST00000390549.6').should('be.visible');
  });
});
