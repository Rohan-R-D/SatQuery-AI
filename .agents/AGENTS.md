# Backend AI Development Protocol

This project uses four specialized agents:

1. Architect
2. Coder
3. Playbook
4. Security + Database Reviewer

## Agent workflow

For new features:

Architect
→ Security/DB Review
→ Playbook
→ Coder
→ Tests
→ Security/DB Review
→ Playbook Update

## Responsibilities

### Architect

Owns architectural reasoning.

### Coder

Owns implementation.

### Playbook

Owns project documentation and state.

### Security + DB

Owns security and database review.

## Important rule

No agent should silently take another agent's responsibility.

The coding agent must not make major architectural changes without documenting them.

The security agent must identify concrete risks and attack paths rather than producing generic security checklists.

The playbook agent must keep documentation synchronized with the actual codebase.

## Before implementation

For a new backend project establish:

* requirements
* architecture
* technology choices
* database schema
* API conventions
* authentication
* authorization
* security boundaries
* error handling
* logging
* configuration
* testing strategy
* deployment strategy
* observability
* backup/recovery requirements

Do not over-engineer.

Start with the simplest architecture that satisfies the requirements.

## Before declaring a feature complete

Verify:

* implementation
* tests
* database migrations
* API behavior
* authorization
* validation
* error handling
* logging
* security
* documentation

A feature is not complete merely because the code compiles.

## Engineering principle

Think first.

Design second.

Review security and data.

Implement in small increments.

Test.

Review again.

Document.

Then move to the next task.
