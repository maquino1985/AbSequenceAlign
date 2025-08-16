describe('MSA Functionality', () => {
  beforeEach(() => {
    cy.visit('/msa-viewer')
  })

  const testSequences = `>seq1
EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS
>seq2
QVQLVQSGAEVKKPGASVKVSCKASGYTFTGYYMHWVRQAPGQGLEWMGWINPNSGGTNYAQKFQGRVTMTRDTSISTAYMELSRLRSDDTAVYYCARATYYYGSRGYAMDYWGQGTLVTVSS`

  it('should upload sequences via text input', () => {
    cy.get('[data-testid="sequence-input"]').type(testSequences)
    cy.get('[data-testid="upload-btn"]').click()
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

  it('should create MSA alignment', () => {
    // Upload sequences first
    cy.get('[data-testid="sequence-input"]').type(testSequences)
    cy.get('[data-testid="upload-btn"]').click()

    // Configure alignment
    cy.get('[data-testid="numbering-scheme"]').select('imgt')
    cy.get('[data-testid="alignment-method"]').select('clustal')
    
    // Start alignment
    cy.get('[data-testid="align-btn"]').click()

    // Check for alignment results
    cy.get('[data-testid="msa-viewer"]', { timeout: 10000 }).should('be.visible')
    cy.get('[data-testid="consensus-sequence"]').should('exist')
    cy.get('[data-testid="conservation-plot"]').should('exist')
  })

  it('should show alignment statistics', () => {
    // Upload and align sequences
    cy.get('[data-testid="sequence-input"]').type(testSequences)
    cy.get('[data-testid="upload-btn"]').click()
    cy.get('[data-testid="align-btn"]').click()

    // Check statistics
    cy.get('[data-testid="statistics-panel"]').should('be.visible')
    cy.get('[data-testid="sequence-count"]').should('contain', '2')
    cy.get('[data-testid="average-identity"]').should('exist')
  })

  it('should handle large alignments with background processing', () => {
    // Generate 20 sequences
    let largeInput = ''
    for (let i = 1; i <= 20; i++) {
      largeInput += `>seq${i}\n${testSequences.split('\n')[1]}\n`
    }

    // Upload sequences
    cy.get('[data-testid="sequence-input"]').type(largeInput)
    cy.get('[data-testid="upload-btn"]').click()

    // Start alignment
    cy.get('[data-testid="align-btn"]').click()

    // Check for job status
    cy.get('[data-testid="job-status"]', { timeout: 20000 }).should('be.visible')
    cy.get('[data-testid="job-status"]').should('contain', 'pending')
  })

  it('should annotate regions in aligned sequences', () => {
    // Upload and align sequences
    cy.get('[data-testid="sequence-input"]').type(testSequences)
    cy.get('[data-testid="upload-btn"]').click()
    cy.get('[data-testid="align-btn"]').click()

    // Wait for alignment and check regions
    cy.get('[data-testid="msa-viewer"]', { timeout: 10000 }).should('be.visible')
    cy.get('[data-testid="region-fr1"]').should('exist')
    cy.get('[data-testid="region-cdr1"]').should('exist')
    cy.get('[data-testid="region-fr2"]').should('exist')
    cy.get('[data-testid="region-cdr2"]').should('exist')
  })

  it('should handle errors gracefully', () => {
    // Test invalid FASTA
    const invalidFasta = '>invalid\nNOTAVALIDSEQUENCE123'
    cy.get('[data-testid="sequence-input"]').type(invalidFasta)
    cy.get('[data-testid="upload-btn"]').click()
    cy.get('[data-testid="error-message"]').should('be.visible')

    // Test empty input
    cy.get('[data-testid="sequence-input"]').clear()
    cy.get('[data-testid="upload-btn"]').click()
    cy.get('[data-testid="error-message"]').should('be.visible')
  })
})
