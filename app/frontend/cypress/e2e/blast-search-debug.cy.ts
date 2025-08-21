describe('BLAST Search Debug Test', () => {
  beforeEach(() => {
    // Visit the BLAST search page
    cy.visit('/')
    
    // Wait for the page to load
    cy.get('h4', { timeout: 10000 }).should('contain', 'BLAST Sequence Search')
  })

  it('should load and display BLAST search interface', () => {
    // Check if the BLAST search interface is loaded
    cy.get('h4').should('contain', 'BLAST Sequence Search')
    cy.get('h6').should('contain', 'BLAST Search Configuration')
  })

  it('should fetch and display databases correctly', () => {
    // Intercept the API call to check the response
    cy.intercept('GET', '**/api/v2/blast/databases').as('getDatabases')
    
    // Wait for the API call to complete
    cy.wait('@getDatabases').then((interception) => {
      // Log the API response for debugging
      cy.log('API Response:', JSON.stringify(interception.response?.body, null, 2))
      
      // Verify the API response structure
      expect(interception.response?.statusCode).to.equal(200)
      expect(interception.response?.body.success).to.be.true
      expect(interception.response?.body.data.databases.public).to.exist
      
      // Check if euk_cdna is in the response
      const publicDbs = interception.response?.body.data.databases.public;
      void expect(publicDbs).to.have.property('euk_cdna');
      void expect(publicDbs.euk_cdna).to.equal('Human+Mouse+Rabbit+Cyno cDNA database');
    })
  })

  it('should display protein databases for BLASTP', () => {
    // Wait for databases to load
    cy.wait(3000)
    
    // Check that BLASTP is selected by default (look for the text in the form)
    cy.contains('BLASTP (Protein vs Protein)').should('be.visible')
    
    // Find and click the database dropdown
    cy.get('label').contains('Database').click()
    
    // Should see protein databases
    cy.get('[role="option"]').should('contain', 'swissprot')
    cy.get('[role="option"]').should('contain', 'pdbaa')
    
    // Should NOT see nucleotide databases
    cy.get('[role="option"]').should('not.contain', 'euk_cdna')
    cy.get('[role="option"]').should('not.contain', 'refseq_select_rna')
  })

  it('should display nucleotide databases for BLASTN', () => {
    // Wait for databases to load
    cy.wait(3000)
    
    // Change to BLASTN - find the BLAST type dropdown and click it
    cy.get('label').contains('BLAST Type').click()
    cy.get('[role="option"]').contains('BLASTN (Nucleotide vs Nucleotide)').click()
    
    // Wait for the change to take effect
    cy.wait(1000)
    
    // Check that nucleotide databases are visible
    cy.get('label').contains('Database').click()
    
    // Should see nucleotide databases
    cy.get('[role="option"]').should('contain', 'euk_cdna')
    cy.get('[role="option"]').should('contain', 'refseq_select_rna')
    cy.get('[role="option"]').should('contain', 'GCF_000001635.27_top_level')
    cy.get('[role="option"]').should('contain', 'GCF_000001405.39_top_level')
    cy.get('[role="option"]').should('contain', '16S_ribosomal_RNA')
    
    // Should NOT see protein databases
    cy.get('[role="option"]').should('not.contain', 'swissprot')
    cy.get('[role="option"]').should('not.contain', 'pdbaa')
  })

  it('should allow database selection and search', () => {
    // Wait for databases to load
    cy.wait(3000)
    
    // Change to BLASTN
    cy.get('label').contains('BLAST Type').click()
    cy.get('[role="option"]').contains('BLASTN (Nucleotide vs Nucleotide)').click()
    
    // Select euk_cdna database
    cy.get('label').contains('Database').click()
    cy.get('[role="option"]').contains('euk_cdna').click()
    
    // Enter a test sequence
    cy.get('textarea').type('ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG')
    
    // Set E-value
    cy.get('input[placeholder*="E-value"]').clear().type('1e-10')
    
    // Set Max Target Sequences
    cy.get('input[placeholder*="Max Target Sequences"]').clear().type('10')
    
    // Click search button
    cy.get('button').contains('Search').click()
    
    // Should show loading state
    cy.get('[role="progressbar"]').should('be.visible')
  })

  it('should handle empty database list gracefully', () => {
    // Intercept and mock empty database response
    cy.intercept('GET', '**/api/v2/blast/databases', {
      statusCode: 200,
      body: {
        success: true,
        message: 'Available databases retrieved successfully',
        data: {
          databases: {
            public: {},
            custom: {},
            internal: {}
          }
        }
      }
    }).as('getEmptyDatabases')
    
    // Reload the page
    cy.reload()
    
    // Wait for the mocked API call
    cy.wait('@getEmptyDatabases')
    
    // Should show appropriate message
    cy.get('label').contains('Database').should('contain', 'No databases available')
  })

  it('should handle API errors gracefully', () => {
    // Intercept and mock error response
    cy.intercept('GET', '**/api/v2/blast/databases', {
      statusCode: 500,
      body: {
        success: false,
        message: 'Internal server error'
      }
    }).as('getErrorDatabases')
    
    // Reload the page
    cy.reload()
    
    // Wait for the mocked API call
    cy.wait('@getErrorDatabases')
    
    // Should show error message
    cy.get('[role="alert"]').should('contain', 'Failed to load')
  })

  it('should validate form inputs correctly', () => {
    // Wait for databases to load
    cy.wait(2000)
    
    // Try to search without sequence
    cy.get('button').contains('Search').click()
    
    // Should show validation error
    cy.get('[role="alert"]').should('contain', 'Please enter')
    
    // Enter invalid sequence
    cy.get('textarea').type('INVALID123')
    cy.get('button').contains('Search').click()
    
    // Should show validation error for invalid sequence
    cy.get('[role="alert"]').should('contain', 'validation')
  })
})
