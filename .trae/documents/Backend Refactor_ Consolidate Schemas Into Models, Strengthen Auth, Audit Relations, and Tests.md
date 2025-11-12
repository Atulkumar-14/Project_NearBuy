## Current State & Key Findings
- FastAPI + SQLAlchemy (async) with SQLite; Pydantic v2 is used.
- SQLAlchemy models live in `app/models/` and Pydantic request/response schemas live in `app/schemas/`.
- Type mismatches exist between schemas and models:
  - `app/schemas/review.py` uses `UUID` ids while `app/models/review.py` uses `int` ids.
  - `app/models/security.py` defines FKs to `Users.user_id` as `uuid` (`GUID`) while `Users.user_id` is `int` (see `app/models/user.py:11`).
- Missing/incorrect definitions:
  - `app/routers/shops.py` imports `ShopInventoryUpdate` but it is not defined in `app/schemas/shop.py`.
  - `app/models/shop.py:is_open` uses `pytz` without import.
  - `app/models/product.py` has a duplicated `__repr__` method on `ShopProduct`.
- Tests are outdated relative to current API:
  - `tests/test_relationships.py` uses `PurchaseHistory`, which does not exist.
  - Owner login tests expect `owner_id+password` but owner login currently uses email-only.

## Folder Structure Refactor
- Remove `app/schemas/` and colocate Pydantic DTOs with their SQLAlchemy models inside `app/models/*` modules.
  - Each model module will expose its SQLAlchemy model(s) and Pydantic DTOs (Create/Update/Read/Login), e.g. in `app/models/user.py` define `User`, `UserCreate`, `UserLogin`, `UserRead`.
  - Move `Token` DTO from `app/schemas/auth.py` into `app/models/auth_dto.py` (new) under `models` for clarity, or colocate with user DTOs if preferred.
- Keep Pythonic naming with `snake_case` files under `app/models/` (consistent, readable), rather than JS-style `*.model.js`.
- Update all router imports from `app.schemas.*` to the new `app.models.*` DTOs.
- Ensure `app/models/__init__.py` re-exports DTOs to centralize imports.

## Authentication Enhancements
- Robust validation and sanitization:
  - Add `field_validator` methods on DTOs for trimming whitespace, normalizing email (`lower()`), and basic phone normalization.
  - Use `EmailStr` for email fields; use constrained `str` types with length checks for names and phone.
  - Implement password policy on signup: min length (12), require upper+lower+digit+symbol; block common passwords.
- Input validation middleware:
  - Add a lightweight dependency that validates content-type and sanitizes common string inputs before handlers.
  - Rate-limit sensitive endpoints (login/register) per IP to mitigate brute force (simple in-memory with `deque`, similar to shop uploads rate limiter).
- Error handling:
  - Return consistent error bodies: `{ "detail": "...", "code": "..." }` with 4xx/5xx as appropriate.
  - Improve messages for invalid credentials, missing fields, and password policy violations.
- Tokens & cookies:
  - Keep existing cookie logic but ensure secure flags honor `settings.require_https`.
  - Confirm role enforcement in `get_current_*` dependencies (already present) and align owner login with the chosen auth flow (email-only or add password depending on business rules).

## Database Relationships Audit & Corrections
- Reconcile FK and ID types:
  - Change `app/models/security.py` to use `int` FKs (`user_id`, `owner_id`) or remove these tables if not part of the business spec; current GUID FKs contradict `Users.user_id:int` and cause FK creation failures.
- Verify and enforce constraints:
  - Ensure all FK columns have `index=True` where filtered (confirmed across `Product`, `ShopProduct`, `ProductReview`, `ShopAddress`, `ShopTiming`).
  - Keep `ondelete="CASCADE"` on mappings that depend on parent rows (already present).
  - Keep `ProductReview.rating` `CheckConstraint` as defined.
- Relationship documentation:
  - Add module-level docstrings per model module documenting relationships:
    - `User` 1:M `ProductReview`, 1:M `SearchHistory`.
    - `ShopOwner` 1:M `Shop`.
    - `Shop` 1:1 `ShopAddress`, 1:M `ShopTiming`, M:M via `ShopProduct` to `Product`.
    - `Product` 1:M `ProductImage`, 1:M `ProductReview`, M:M via `ShopProduct` to `Shop`; M:1 `ProductCategory`.
- Minor fixes:
  - Import `pytz` in `app/models/shop.py` for `is_open` or refactor to use locale-agnostic time; add graceful handling when timings are missing.
  - Remove duplicate `__repr__` in `app/models/product.py` for `ShopProduct`.

## Error Handling & Testing
- Type consistency fixes:
  - Align DTO id types to `int`, update routers to use DTOs from `models`.
- Unit tests:
  - Replace `PurchaseHistory` test with FK integrity tests on existing M:M (`ShopProduct`) and 1:M (`ProductReview`) to verify invalid FK inserts fail.
  - Update owner login tests to match chosen flow (email-only or email+password if we introduce owner passwords).
  - Add tests for:
    - User signup validation: weak password rejection, invalid email rejection, duplicate email/phone rejection.
    - Login: wrong password, non-existent user, cookie issuance.
    - Shop/product endpoints: creation, inventory updates, and validation errors.
- Error propagation:
  - Use `try/except` around DB commits where appropriate to convert `IntegrityError` into 409 with meaningful `detail`.
  - Keep non-blocking logging around notifications and realtime broadcasting.

## Code Quality Standards
- Consistent Python style: `snake_case` filenames, type hints, and Pydantic v2 configs (`ConfigDict(from_attributes=True)` or `class Config: from_attributes=True`) uniformly.
- Docstrings: add clear class and method docstrings across models and DTOs detailing purpose and relationships.
- Separation of concerns:
  - Keep business rules in routers/services; keep data structure definitions (SQLAlchemy + Pydantic DTOs) in `models`.
  - Security helpers remain in `app/core/security.py`; auth dependencies in `app/core/auth.py`.
- Backward compatibility:
  - API shapes remain the same where already defined with `response_model`.
  - Internal imports updated; external clients unaffected.

## Implementation Plan (Phased)
1) Prepare DTOs in `app/models/*`:
- Add `UserCreate`, `UserLogin`, `UserRead` to `user.py` with validators (email normalization, password policy).
- Add `ProductCreate`, `ProductRead` to `product.py`; fix duplicate `__repr__`.
- Add `ReviewCreate`, `ReviewRead` to `review.py` with `int` ids.
- Add `ShopCreate`, `ShopRead`, `ShopRegister`, `ShopProductAdd`, `ShopInventoryUpdate` to `shop.py`; import `pytz` for `is_open` or refactor.
- Add `OwnerLogin`, `OwnerRead` to `owner.py`.
- Add `Token` DTO to `app/models/auth_dto.py` and update imports.

2) Update routers to import DTOs from `app/models/*` and improve validation:
- Strengthen `/api/auth/register` and `/api/auth/login` with DTO validators and richer error messages.
- Convert DB integrity errors to 409 and return structured errors.
- Add simple per-IP rate limiting for `/api/auth/login` and `/api/auth/register` (mirroring image upload limiter).

3) Fix relationships & types:
- Change `app/models/security.py` FK types to `int` (or remove tables if not part of spec).
- Ensure all FK columns have `index=True`; keep CASCADE.
- Add module-level docstrings documenting relationships.

4) Delete `app/schemas/` and update internal imports:
- After DTOs are colocated and routers updated, remove the folder.
- Verify `main.py` and all routers compile and run.

5) Tests & verification:
- Update existing tests to current API and add new coverage for validation and relationships.
- Run the test suite; fix any regressions.
- Manual smoke test of auth/login/register and core shop/product APIs.

## Risks & Mitigations
- Removing `schemas/` requires careful update of imports; mitigated by doing a global search and update.
- Changing `security.py` types may require DB migration; since these tables are not in `models/__init__.py` they likely aren’t created—safe to fix and include or omit per requirements.
- Password policy may break weak seeded defaults; update seeds to meet new policy.

## Confirmation
If this plan looks good, I will proceed to implement it step-by-step, verify with tests, and keep all API endpoints backward compatible while consolidating DTOs under `app/models/`.