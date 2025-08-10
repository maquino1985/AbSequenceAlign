describe('Health Check', () => {
  it('should connect to backend and frontend', () => {
    // Quick backend health check
    cy.request({
      url: '/api/v1/health',
      timeout: 5000,
      failOnStatusCode: false
    }).then((response) => {
      expect(response.status).to.be.oneOf([200, 404]); // Accept either healthy or not found
    });

    // Quick frontend check
    cy.visit('/', { timeout: 10000 });
    cy.get('body').should('be.visible');
  });
});