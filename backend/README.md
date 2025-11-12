Nearbuy Backend

Authentication and Authorization
- Owner Login: uses `email` and `password` (token `sub` is owner UUID).
- User Login: returns JWT with role `user` (token `sub` is user UUID).
- Admin Login: returns JWT with role `admin` and subject `admin:<userId>`.
- Admin endpoints are protected by middleware and dependency checks enforcing admin role and logging all access attempts.
 - Two-factor authentication (2FA) for owners has been removed. Login requires only email and password; related endpoints are deprecated.

Database Schema Relationships
- `Users` 1—N `Product_Reviews` (`Product_Reviews.user_id` → `Users.user_id`).
- `Users` 1—N `Search_History` (`Search_History.user_id` → `Users.user_id`).
- `Users` 1—N `Purchase_History` (`Purchase_History.user_id` → `Users.user_id`).
- `Product_Categories` 1—N `Products` (`Products.category_id` → `Product_Categories.category_id`).
- `Products` 1—N `Product_Images` (`Product_Images.product_id` → `Products.product_id`).
- `Products` 1—N `Product_Reviews` (`Product_Reviews.product_id` → `Products.product_id`).
- `Shops` 1—N `Shop_Product` (`Shop_Product.shop_id` → `Shops.shop_id`).
- `Products` 1—N `Shop_Product` (`Shop_Product.product_id` → `Products.product_id`).
- `Shop_Owners` 1—N `Shops` (`Shops.owner_id` → `Shop_Owners.owner_id`).
- `Shops` 1—1 `Shop_Address` (`Shop_Address.shop_id` → `Shops.shop_id`).
- `Shops` 1—N `Shop_Timings` (`Shop_Timings.shop_id` → `Shops.shop_id`).
- All FKs enforce `ON DELETE CASCADE` where reasonable; SQLite foreign keys are enabled via PRAGMA.
- All IDs are UUIDs stored as 16-byte binary via custom `GUID` type.

Dummy Accounts for Testing
- Configure credentials in `.env` (values shown are defaults used if not set):
  - `ADMIN_USER_ID=nearbuy-admin`
  - `ADMIN_PASSWORD=Admin@123`
  - `OWNER_DUMMY_NAME=Demo Owner`
  - `OWNER_DUMMY_EMAIL=owner.demo@example.com`
  - `OWNER_DUMMY_PHONE=9000000000`
  - `OWNER_DUMMY_PASSWORD=Owner@123`
  - `USER_DUMMY_NAME=Demo User`
  - `USER_DUMMY_EMAIL=user.demo@example.com`
  - `USER_DUMMY_PHONE=7000000000`
  - `USER_DUMMY_PASSWORD=Password@123`
- Passwords are hashed when stored in the database.
- Owner login uses the dummy owner `email` and `password`.

Testing Notes
- Unit tests should cover user, owner, and admin login flows and negative cases.
- Admin endpoint tests should verify role-based rejection and acceptance.
- Integration tests should exercise FK relationships by attempting invalid inserts and expecting integrity errors.

Seeding
- Run `python -m app.seed` from the `backend` directory to insert dummy data.

UUID Migration Notes
- All primary keys and foreign keys are UUIDs across models and schemas.
- FastAPI routes accept UUIDs for IDs (e.g. `user_id`, `shop_id`, `product_id`).
- JWT tokens carry UUID `sub` for users and owners; admins use `admin:<userId>`.
- SQLAlchemy `GUID` TypeDecorator stores UUIDs as BINARY(16) in SQLite.

How to Migrate / Reset Locally
- If an old SQLite file exists, delete `backend/nearbuy.db` to recreate:
  - PowerShell: `Remove-Item -Force .\backend\nearbuy.db`
- Start the app to initialize tables, then reseed:
  - From `backend`: `python -m app.seed`

Indexes
- Unique: `Users.email`, `Users.phone`, `Shop_Owners.email`, `Shop_Owners.phone`, `admin.userId`, `Shops.gstin`.
- Foreign keys indexed: `Products.category_id`, `Product_Images.product_id`, `Product_Reviews.user_id`, `Product_Reviews.product_id`, `Shop_Product.shop_id`, `Shop_Product.product_id`, `Shop_Address.shop_id`, `Shop_Timings.shop_id`, `Purchase_History.user_id`, `Purchase_History.shop_id`, `Purchase_History.product_id`.


API Endpoints Overview
- `GET /` — API health check. Returns `{ message: "Nearbuy API is running" }`.
- `GET /api/metrics` — Monitoring summary. Returns endpoint counts, status code counts, and timing stats.

- Auth
  - `POST /api/auth/register` — Register user. Request: `{ name, email, password, phone }`. Returns `UserRead`. Errors: `400` if duplicate.
  - `POST /api/auth/login` — User login with `{ email, password }`. Returns `Token` and sets `user_access_token` and `user_refresh_token` cookies. Errors: `401` invalid.
  - `POST /api/auth/owner/login` — Owner login with `{ email, password }`. Returns `Token` and sets cookies. Errors: `400/401` invalid.
  - `POST /api/auth/admin/login` — Admin login with `{ userId, password }`. Returns `Token`. Errors: `401` invalid.
  - `POST /api/auth/refresh` — Refresh cookie-based token. Returns `{ status: "ok" }` and sets new cookies. Errors: `401` invalid/missing.
  - `POST /api/auth/logout` — Clears user and owner cookies. Returns `{ status: "logged_out" }`.

- Users
  - `GET /api/users` — List users. Returns `UserRead[]`.
  - `GET /api/users/me` — Current user profile. Requires `Authorization: Bearer <token>` or valid `user_access_token` cookie with matching role. Returns `UserRead`.
  - `GET /api/users/{user_id}/purchases` — Purchase history for user. Returns array of purchase records.

- Admin
  - `GET /api/admin/stats` — Summary counts (users, shops, products, reviews). Requires admin role. Errors: `401/403`.

- Shops/Products/Reviews/Search/Uploads/Owners
  - See routers in `app/routers/` for CRUD operations and details.


Deployment Instructions
- Development
  - Python: `cd backend && uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000`
  - Seed: `python -m app.seed`
  - Frontend: `cd frontend && npm install && npm run dev`
- Production (example)
  - Run with `uvicorn` behind a reverse proxy (e.g., Nginx). Configure HTTPS if `require_https=True`.
  - Ensure environment variables via `.env` (see settings in `app/core/config.py`).
  - Use a production database (PostgreSQL recommended) and proper migrations.


Testing
- Python tests: `cd backend && pytest -q`
  - Unit tests cover auth flows and admin security.
  - Relationship tests validate foreign key constraints.
- Performance (Locust)
  - Install: `pip install locust`
  - Run: `cd backend/scripts && locust -f locustfile.py` then open `http://localhost:8089`.
- End-to-end (Frontend, Playwright)
  - Install dev dependency: `npm i -D @playwright/test`
  - Add tests under `frontend/tests/` and run with `npx playwright test`.


Operational Monitoring
- Use `GET /api/metrics` to view request counts and latencies.
- Extend logging/observability in `app/middleware/metrics.py` as needed.