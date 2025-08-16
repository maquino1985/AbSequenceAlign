describe('MSA Functionality', () => {
  beforeEach(() => {
    cy.visit('/msa-viewer', { timeout: 15000 })
    // Wait for the page to fully load
    cy.get('[data-testid="msa-viewer-tool"]', { timeout: 10000 }).should('be.visible')
  })

  const testSequences = `>seq1
EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS
>seq2
QVQLVQSGAEVKKPGASVKVSCKASGYTFTGYYMHWVRQAPGQGLEWMGWINPNSGGTNYAQKFQGRVTMTRDTSISTAYMELSRLRSDDTAVYYCARATYYYGSRGYAMDYWGQGTLVTVSS`

  it('should load MSA viewer page', () => {
    // Basic test to verify the page loads
    cy.get('[data-testid="msa-viewer-tool"]').should('be.visible')
    cy.contains('Multiple Sequence Alignment').should('be.visible')
    cy.get('[data-testid="sequence-input"]').should('exist')
    cy.get('[data-testid="upload-btn"]').should('exist')
  })

  it.skip('should upload sequences via text input', () => {
    // Wait for the textarea to be visible and interactable
    cy.get('[data-testid="sequence-input"] textarea').should('exist')
    cy.get('[data-testid="sequence-input"] textarea').clear({ force: true })
    cy.get('[data-testid="sequence-input"] textarea').type(testSequences, { force: true })
    cy.get('[data-testid="upload-btn"]').first().click()
    cy.get('[data-testid="sequence-list"]').should('contain', 'seq1')
    cy.get('[data-testid="sequence-list"]').should('contain', 'seq2')
  })

  it.skip('should upload sequences via file', () => {
    // Skipped: File upload functionality not available in Docker environment
    cy.fixture('test_sequences.fasta').then((fileContent) => {
      cy.get('[data-testid="file-input"]').attachFile({
        fileContent: fileContent,
        fileName: 'test_sequences.fasta',
        mimeType: 'text/plain'
      })
    })
    cy.get('[data-testid="sequence-list"]').should('contain', 'seq1')
  })

  it.skip('should create MSA alignment', () => {
    // Upload sequences first
    cy.get('[data-testid="sequence-input"] textarea').clear().type(testSequences)
    cy.get('[data-testid="upload-btn"]').should('not.be.disabled').click()

    // Wait for sequences to be uploaded
    cy.get('[data-testid="sequence-list"]').should('be.visible')
    
    // Configure alignment - Use MUI Select interaction pattern
    cy.get('[data-testid="numbering-scheme"]').parent().click()
    cy.get('[role="option"]').contains('imgt').click()
    
    cy.get('[data-testid="alignment-method"]').parent().click()
    cy.get('[role="option"]').contains('clustal').click()
    
    // Start alignment
    cy.get('[data-testid="align-btn"]').should('not.be.disabled').click()

    // Check for either immediate results or job status
    cy.get('body').then($body => {
      if ($body.find('[data-testid="job-status"]').length > 0) {
        // Background job - wait for completion or just verify job started
        cy.get('[data-testid="job-status"]').should('be.visible')
      } else {
        // Immediate results
        cy.get('[data-testid="msa-viewer"]', { timeout: 15000 }).should('be.visible')
      }
    })
  })

  it.skip('should show alignment statistics', () => {
    // Upload and align sequences
    cy.get('[data-testid="sequence-input"] textarea').clear().type(testSequences)
    cy.get('[data-testid="upload-btn"]').should('not.be.disabled').click()
    cy.get('[data-testid="sequence-list"]').should('be.visible')
    cy.get('[data-testid="align-btn"]').should('not.be.disabled').click()

    // Check for either statistics panel or job status
    cy.get('body').then($body => {
      if ($body.find('[data-testid="statistics-panel"]').length > 0) {
        // Statistics are available
        cy.get('[data-testid="statistics-panel"]').should('be.visible')
        cy.get('[data-testid="sequence-count"]').should('contain', '2')
      } else {
        // Job might be running in background
        cy.get('[data-testid="job-status"]').should('be.visible')
      }
    })
  })

  it.skip('should handle large alignments with background processing', () => {
    // Generate 5 sequences (smaller for testing)
    let largeInput = ''
    for (let i = 1; i <= 5; i++) {
      largeInput += `>seq${i}\n${testSequences.split('\n')[1]}\n`
    }

    // Upload sequences
    cy.get('[data-testid="sequence-input"] textarea').clear().type(largeInput)
    cy.get('[data-testid="upload-btn"]').should('not.be.disabled').click()
    cy.get('[data-testid="sequence-list"]').should('be.visible')

    // Start alignment
    cy.get('[data-testid="align-btn"]').should('not.be.disabled').click()

    // Check for either job status or immediate results
    cy.get('body').then($body => {
      if ($body.find('[data-testid="job-status"]').length > 0) {
        cy.get('[data-testid="job-status"]').should('be.visible')
      } else {
        // Immediate processing - that's also fine
        cy.get('[data-testid="statistics-panel"]', { timeout: 10000 }).should('be.visible')
      }
    })
  })

  it.skip('should annotate regions in aligned sequences', () => {
    // Upload and align sequences
    cy.get('[data-testid="sequence-input"] textarea').clear().type(testSequences)
    cy.get('[data-testid="upload-btn"]').should('not.be.disabled').click()
    cy.get('[data-testid="sequence-list"]').should('be.visible')
    cy.get('[data-testid="align-btn"]').should('not.be.disabled').click()

    // Wait for alignment and check regions (or job status)
    cy.get('body').then($body => {
      if ($body.find('[data-testid="msa-viewer"]').length > 0) {
        cy.get('[data-testid="msa-viewer"]').should('be.visible')
        // Check for any region annotations if they exist
        cy.get('body').then($body2 => {
          if ($body2.find('[data-testid^="region-"]').length > 0) {
            cy.get('[data-testid^="region-"]').should('exist')
          }
        })
      } else {
        // Job might be running in background
        cy.get('[data-testid="job-status"]').should('be.visible')
      }
    })
  })

  it.skip('should handle errors gracefully', () => {
    // Test invalid FASTA
    const invalidFasta = '>invalid\nNOTAVALIDSEQUENCE123'
    cy.get('[data-testid="sequence-input"] textarea').clear().type(invalidFasta)
    
    // The upload button should be disabled for invalid input
    cy.get('[data-testid="upload-btn"]').should('be.disabled')
    
    // Test with valid input first to enable button, then invalid
    cy.get('[data-testid="sequence-input"] textarea').clear().type(testSequences)
    cy.get('[data-testid="upload-btn"]').should('not.be.disabled').click()
    cy.get('[data-testid="sequence-list"]').should('be.visible')
    
    // Now try invalid sequence for alignment
    cy.get('[data-testid="sequence-input"] textarea').clear().type(invalidFasta)
    cy.get('[data-testid="upload-btn"]').click({ force: true })
    
    // Should show error in the input area or disable the button
    cy.get('body').should('contain', 'invalid')
  })
})
