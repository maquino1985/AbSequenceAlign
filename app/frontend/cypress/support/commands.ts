/// <reference types="cypress" />

declare global {
  namespace Cypress {
    interface Chainable {
      getBySel(selector: string, ...args: any[]): Chainable<JQuery<HTMLElement>>;
    }
  }
}

Cypress.Commands.add('getBySel', (selector: string, ...args: any[]) => {
  return cy.get(`[data-testid=${selector}]`, ...args);
});

export {};