Selenium E2E Tests for Frontend

Overview
- Verifies search, user interactions, shops nearby (geolocation), and city change flows.
- Uses explicit waits, assertions, and captures screenshots/HTML/network logs on failures.
- Supports headless/headed mode via environment variables.

Prerequisites
- Google Chrome installed.
- Python 3.10+ installed.
- Install dependencies:
  - pip install selenium pytest
  - pip install requests  # optional: used for metrics verification
  - Optional: pip install webdriver-manager (if you prefer auto driver management)

Environment
- FRONTEND_BASE_URL: Base URL of the running frontend (default: `http://localhost:5173/`).
- HEADLESS: `true` or `false` (default: `true`).
- SELENIUM_REPORT_DIR: Directory for artifacts (default: `frontend/selenium_reports`).
- USER_EMAIL / USER_PASSWORD: Credentials for user login (defaults: `user.demo@example.com` / `Password@123`).
- OWNER_ID / OWNER_PASSWORD: Credentials for owner login (defaults: `owner_001` / `Owner@5678`).

Start Frontend
- Ensure the frontend dev server is running and accessible at `FRONTEND_BASE_URL`.
  - For Vite, typically: `npm run dev` and open `http://localhost:5173/`.

Optional Backend
- Tests confirm API calls by reading Chrome performance logs. Backend is not strictly required, but enabling it improves UI assertions (e.g., Nearby Shops section).
- Backend dev server: `uvicorn backend.main:app --reload` listening at `http://localhost:8000/`.

Run Tests
- Headless (default):
  - `pytest frontend/tests/selenium_e2e_test.py -q`
- Headed:
  - `HEADLESS=false pytest frontend/tests/selenium_e2e_test.py -q`
- Custom base URL:
  - `FRONTEND_BASE_URL=http://localhost:3000/ pytest frontend/tests/selenium_e2e_test.py -q`
- Custom credentials:
  - `USER_EMAIL=testuser@example.com USER_PASSWORD=Test@1234 OWNER_ID=owner_001 OWNER_PASSWORD=Owner@5678 pytest frontend/tests/selenium_e2e_test.py -q`

Artifacts
- On failures, screenshots, HTML snapshots, and network JSON logs are saved to `SELENIUM_REPORT_DIR`.

Notes
- Geolocation is mocked via CDP for the origin defined by `FRONTEND_BASE_URL`.
- If Chrome denies geolocation in your environment, the test still validates API calls but Nearby Shops UI may not render.
- Owner login UI uses Owner email (aligned with backend `/api/auth/owner/login`).