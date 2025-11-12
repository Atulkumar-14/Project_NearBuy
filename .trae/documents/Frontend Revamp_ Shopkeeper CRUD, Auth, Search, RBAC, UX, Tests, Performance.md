## Overview

* Validate the completed refactor under `backend/app/models/`, confirm `schemas` removal and updated imports.

* Execute and fix tests; perform API smoke tests; verify auth, relationships, and error handling behave as designed.

## Structure Validation

* Verify DTOs co-located with SQLAlchemy models; imports use `app.models.*` exclusively.

* Check naming conventions consistency and `app/models/__init__.py` exports.

* Confirm FK types, `ondelete="CASCADE"`, indexes, and relationship definitions in `user.py`, `product.py`, `review.py`, `shop.py`, `security.py`.

## Test Setup

* Create/activate a backend virtual environment; install test deps: `pytest`, `httpx`, `fastapi`, `sqlalchemy`, `python-jose`, `passlib`, `pydantic>=2`.

* Run `pytest -q` in `backend`; capture failures for iterative fixes.

## Fix & Adjust

* Address failing tests: align DTO validators and router responses, fix residual type mismatches (e.g., `int` IDs vs GUIDs), and any serialization issues (`EmailStr`).

* Ensure rate limiter does not cause test flakiness; gate via config/env if needed.

* Tighten error propagation and consistent status codes/messages where discrepancies appear.

## API Smoke Tests

* Launch the app (`uvicorn main:app`) and exercise core endpoints:

  * `POST /auth/register` and `POST /auth/login` using `UserCreate` and returning `Token`/`UserRead`.

  * Product CRUD: create/list/detail with `ProductCreate`/`ProductRead`.

  * Reviews: create/list with `ReviewCreate`/`ReviewRead`.

  * Shops and inventory: register/shop CRUD, add product, update inventory.

* Validate response shapes and backward compatibility.

## Security & Validation

* Verify password strength enforcement and email normalization/sanitization.

* Confirm per-IP rate limiting behavior and `429` responses with clear messages.

* Check JWT issuance/verification, cookie handling, and role-based access where applicable.

## Documentation & Quality

* Ensure module-level relationship docstrings exist and are accurate in all model files.

* Add/align JSDoc-like docstrings for models/methods where missing; enforce consistent style and separation of concerns.

* Maintain backward-compatible API responses and error formats.

## Deliverables

* Passing test suite and a brief smoke-test summary.

* Summary of relationship audit and type fixes.

* Minimal diffs for any code adjustments made during validation.

