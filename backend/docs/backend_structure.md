# Backend Structure Report

This document summarizes the backend project's structure, responsibilities, and
major flows. It focuses on how the code is organized and how the main features
are implemented.

## High-Level Architecture

- API layer (FastAPI): request/response schemas, routing, auth dependencies.
- Application layer: use cases and DTOs (orchestrates domain behavior).
- Domain layer: entities, value objects, and domain validation rules.
- Infra layer: external services (OpenAI LLM), stub implementations.
- DI container: wiring of use cases, repositories, and LLM adapters.

## Directory Overview

- `app/api/http/routers/`
  - HTTP routes for Auth, Profile, Target, Meal, Nutrition, DailyReport, Billing.
  - Uses Pydantic schemas and auth dependencies.
- `app/api/http/schemas/`
  - Request/response models used by routers.
- `app/api/http/dependencies/`
  - Auth-related dependencies for current user extraction.
- `app/application/`
  - Use cases and DTOs for each domain.
- `app/domain/`
  - Entities and value objects for auth, profile, target, meal, nutrition, billing.
  - Validation rules live in `__post_init__` or dedicated methods.
- `app/infra/llm/`
  - OpenAI-based implementations (target, estimator, daily report).
  - Stub implementations for non-LLM environments.
- `app/di/container.py`
  - Dependency injection wiring and feature toggles (OpenAI vs stub).
- `docs/openapi/openapi.yaml`
  - OpenAPI specification for the REST API.
- `tests/`
  - Unit tests and real integration tests.

## Core Domains and Responsibilities

### Auth
- Registration, login, refresh, logout.
- Cookie-based auth: ACCESS_TOKEN and REFRESH_TOKEN.
- Auth dependencies resolve current user for protected endpoints.

### Profile
- Create/update and fetch current user's profile.
- Stores sex, birthdate, height, weight, meals_per_day.

### Target (Daily Nutrient Targets)
- Create/list/get/update/activate targets.
- Target generation uses LLM (OpenAI) or stub based on environment flags.
- Target data includes nutrients, rationale, and disclaimer.

### Meal (Food Entries)
- CRUD for individual food entries (`/meal-items`).
- Supports main meals (meal_index) and snacks (meal_index is null).
- Updates recompute daily nutrition summaries for impacted dates.

### Nutrition
- `/nutrition/meal` recomputes meal and daily nutrition summaries.
- Daily nutrition summaries aggregate nutrient intake across meals.

### Daily Report
- `/nutrition/daily/report` generates or fetches daily report text.
- LLM output is validated and mapped into DTOs.

### Billing (Stripe)
- Checkout session creation.
- Billing portal URL generation.
- Stripe webhook handling for subscription updates.

## API Endpoints (Summary)

- Auth: `/auth/register`, `/auth/login`, `/auth/logout`, `/auth/refresh`, `/auth/me`
- Profile: `/profile/me` (GET/PUT)
- Target: `/targets`, `/targets/active`, `/targets/{target_id}`,
  `/targets/{target_id}/activate`
- Meal: `/meal-items` (POST/GET), `/meal-items/{entry_id}` (PATCH/DELETE)
- Nutrition: `/nutrition/meal`, `/nutrition/daily/report` (POST/GET)
- Billing: `/billing/checkout-session`, `/billing/portal-url`,
  `/billing/stripe/webhook`

## LLM (OpenAI) Integration

- Implementations in `app/infra/llm/`.
- OpenAI usage is configured via environment variables and DI container.
- Key implementations:
  - Target generation (daily nutrient targets).
  - Meal-level nutrition estimator.
  - Daily report generator.

## Dependency Injection and Feature Toggles

- `app/di/container.py` provides singleton instances.
- Feature toggles select OpenAI or stub implementations:
  - `USE_OPENAI_TARGET_GENERATOR`
  - `USE_OPENAI_NUTRITION_ESTIMATOR`
  - `USE_OPENAI_DAILY_REPORT_GENERATOR`
  - Model selection via `OPENAI_*_MODEL`.

## Testing

- Unit tests for core logic and OpenAI adapters in `tests/unit/`.
- Real integration tests in `tests/integration_real/` (requires auth and
  `OPENAI_API_KEY` when LLM is invoked).

## Notes on Data Flow

- Authenticated requests use cookie-based session tokens.
- Target creation depends on profile data; LLM generates recommended nutrients.
- Nutrition summaries are recomputed after meal updates.
- Daily reports depend on profile, targets, and daily nutrition summaries.
