# Changelog

## Phase 1: Foundation
* Project scaffolding with `uv`.
* Async PostgreSQL setup with SQLAlchemy 2.0.
* Standardized response middleware with Trace IDs.

## Phase 2: Security
* Pure JSON Authentication implementation.
* Migration to `pwdlib` and Argon2.
* JWT implementation with standard `sub` claims.

## Phase 3: Meeting Management
* Meeting CRUD implementation.
* Ownership and authorization logic.

## Phase 4: AI & Analysis
* OpenAI integration with Structured Outputs.
* Meeting analysis endpoint.
* Citation-based grounding strategy.

## Phase 5: Action Items & Reminders
* Action item extraction and tracking.
* APScheduler background job implementation.
* Discord Webhook integration for overdue reminders.

## Phase 6: Finalization
* Evaluation metadata endpoint.
* Comprehensive Unit and Integration test suite.
* Makefile and Docker support.
* Full project documentation.
