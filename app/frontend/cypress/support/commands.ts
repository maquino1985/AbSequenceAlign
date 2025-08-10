/// <reference types="cypress" />

declare module 'cypress' {
  interface Chainable {
    getBySel(selector: string, ...args: unknown[]): Chainable<JQuery<HTMLElement>>;
  }
}

Cypress.Commands.add('getBySel', (selector: string, ...args: unknown[]) => {
  return cy.get(`[data-testid=${selector}]`, ...args);
});

export {};