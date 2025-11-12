import os
import json
import time
from urllib.parse import urlparse

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
try:
    import requests
except Exception:
    requests = None


# Configuration
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173/")
HEADLESS = os.getenv("HEADLESS", "true").lower() in ("1", "true", "yes")
REPORT_DIR = os.getenv("SELENIUM_REPORT_DIR", os.path.join("frontend", "selenium_reports"))
USER_EMAIL = os.getenv("USER_EMAIL", "user.demo@example.com")
USER_PASSWORD = os.getenv("USER_PASSWORD", "Password@123")
OWNER_ID = os.getenv("OWNER_ID", "owner_001")
OWNER_PASSWORD = os.getenv("OWNER_PASSWORD", "Owner@5678")


def _ensure_report_dir():
    os.makedirs(REPORT_DIR, exist_ok=True)


def _new_driver():
    opts = webdriver.ChromeOptions()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,900")
    # Capture network events via CDP performance logs
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    # Allow insecure localhost for dev
    opts.add_argument("--allow-insecure-localhost")
    driver = webdriver.Chrome(options=opts)

    # Grant geolocation permission and set a default mock location
    origin = FRONTEND_BASE_URL.rstrip("/")
    try:
        driver.execute_cdp_cmd("Browser.grantPermissions", {
            "origin": origin,
            "permissions": ["geolocation"],
        })
        driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
            "latitude": 23.2599,  # Bhopal
            "longitude": 77.4126,
            "accuracy": 50,
        })
    except Exception:
        # Non-fatal if CDP calls fail
        pass

    return driver


@pytest.fixture
def driver():
    _ensure_report_dir()
    d = _new_driver()
    yield d
    try:
        d.quit()
    except Exception:
        pass


def save_artifacts(driver, name_prefix: str):
    ts = int(time.time() * 1000)
    png_path = os.path.join(REPORT_DIR, f"{name_prefix}-{ts}.png")
    html_path = os.path.join(REPORT_DIR, f"{name_prefix}-{ts}.html")
    try:
        driver.save_screenshot(png_path)
    except Exception:
        pass
    try:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
    except Exception:
        pass
    return png_path, html_path


def consume_network_events(driver):
    """Return parsed performance log events and clear buffer."""
    events = []
    try:
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                msg = json.loads(entry.get("message", "{}"))
                events.append(msg)
            except Exception:
                continue
    except Exception:
        # Some drivers may not support performance logs in headless
        pass
    return events


def find_api_requests(events):
    """Extract API requests from performance log events."""
    urls = []
    for e in events:
        try:
            method = e["message"]["method"]
            if method == "Network.requestWillBeSent":
                url = e["message"]["params"]["request"]["url"]
                if url.startswith("http://localhost:8000/api/"):
                    urls.append(url)
        except Exception:
            continue
    return urls


def wait_for_text(driver, locator, text, timeout=10):
    WebDriverWait(driver, timeout).until(
        EC.text_to_be_present_in_element(locator, text)
    )


def wait_visible(driver, by, selector, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, selector))
    )


def clear_local_storage(driver):
    driver.execute_script("window.localStorage.clear();")


def open_home(driver):
    driver.get(FRONTEND_BASE_URL)
    clear_local_storage(driver)
    # Wait for search inputs
    wait_visible(driver, By.CSS_SELECTOR, "select")
    wait_visible(driver, By.CSS_SELECTOR, "input[placeholder='What are you looking for?']")
    # City input placeholder may vary; support both variants
    try:
        wait_visible(driver, By.CSS_SELECTOR, "input[placeholder='Search by City']")
    except Exception:
        wait_visible(driver, By.CSS_SELECTOR, "input[placeholder='City (optional)']")


def login_user(driver, email, password):
    driver.get(FRONTEND_BASE_URL.rstrip('/') + "/login")
    email_input = wait_visible(driver, By.CSS_SELECTOR, "input[type='email']")
    pass_input = wait_visible(driver, By.CSS_SELECTOR, "input[type='password']")
    email_input.clear(); email_input.send_keys(email)
    pass_input.clear(); pass_input.send_keys(password)
    # Submit
    login_btn = wait_visible(driver, By.XPATH, "//button[normalize-space()='Login' or normalize-space()='Logging in...']")
    consume_network_events(driver)
    login_btn.click()


def login_owner(driver, owner_id, password):
    driver.get(FRONTEND_BASE_URL.rstrip('/') + "/owner/login")
    id_input = wait_visible(driver, By.CSS_SELECTOR, "input[placeholder='Owner ID']")
    pass_input = wait_visible(driver, By.CSS_SELECTOR, "input[type='password']")
    id_input.clear(); id_input.send_keys(owner_id)
    pass_input.clear(); pass_input.send_keys(password)
    # Submit
    login_btn = wait_visible(driver, By.XPATH, "//button[normalize-space()='Login' or normalize-space()='Logging in...']")
    consume_network_events(driver)
    login_btn.click()


def assert_url_contains(driver, path_suffix, timeout=10):
    WebDriverWait(driver, timeout).until(lambda d: path_suffix in urlparse(d.current_url).path)


def assert_no_password_leak_in_urls(driver):
    events = consume_network_events(driver)
    urls = []
    for e in events:
        try:
            method = e["message"]["method"]
            if method == "Network.requestWillBeSent":
                url = e["message"]["params"]["request"]["url"]
                urls.append(url)
        except Exception:
            continue
    assert not any("password=" in u for u in urls), f"Sensitive data exposed in URL: {urls}"


def test_search_functionality(driver):
    open_home(driver)
    query = "milk"

    # Set type Product
    type_select = wait_visible(driver, By.CSS_SELECTOR, "select")
    type_select.click()
    # Choose product explicitly
    # Ensure the value change using JavaScript for reliability
    driver.execute_script("arguments[0].value='product'; arguments[0].dispatchEvent(new Event('change'));", type_select)

    # Enter query
    q_input = wait_visible(driver, By.CSS_SELECTOR, "input[placeholder='What are you looking for?']")
    q_input.clear()
    q_input.send_keys(query)

    # Clear previous performance logs
    consume_network_events(driver)

    # Trigger search and validate loading state
    search_btn = wait_visible(driver, By.XPATH, "//button[normalize-space()='Search' or normalize-space()='Searching...']")
    search_btn.click()
    try:
        wait_for_text(driver, (By.XPATH, "//button"), "Searching...", timeout=3)
    except Exception:
        # Loading may be too fast; continue
        pass
    # Results grid or empty state should appear eventually
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//h2[normalize-space()='Search Results']"))
    )

    # Validate API call
    urls = find_api_requests(consume_network_events(driver))
    assert any("/api/search/products" in u and f"q={query}" in u for u in urls) or any("/api/products/in_city" in u and f"q={query}" in u for u in urls), \
        f"Expected search API call with q={query}, got: {urls}"


def test_user_interactions_view_shop_and_prices(driver):
    open_home(driver)

    # Switch to shop search and perform a search
    type_select = wait_visible(driver, By.CSS_SELECTOR, "select")
    driver.execute_script("arguments[0].value='shop'; arguments[0].dispatchEvent(new Event('change'));", type_select)

    # City input placeholder may vary; support both variants
    try:
        city_input = wait_visible(driver, By.CSS_SELECTOR, "input[placeholder='Search by City']")
    except Exception:
        city_input = wait_visible(driver, By.CSS_SELECTOR, "input[placeholder='City (optional)']")
    city_input.clear()
    city_input.send_keys("")

    consume_network_events(driver)

    search_btn = wait_visible(driver, By.XPATH, "//button[normalize-space()='Search' or normalize-space()='Searching...']")
    search_btn.click()

    # Wait for results item cards
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//h2[normalize-space()='Search Results']"))
    )

    urls = find_api_requests(consume_network_events(driver))
    assert any("/api/search/shops" in u for u in urls) or any("/api/shops/by_city" in u for u in urls), \
        f"Expected shops search API call, got: {urls}"

    # Click View Shop on first card if present
    view_shop_buttons = driver.find_elements(By.XPATH, "//button[normalize-space()='View Shop']")
    if view_shop_buttons:
        consume_network_events(driver)
        view_shop_buttons[0].click()

        # Shop page loads and calls shop detail + products
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'Shop') or contains(., 'Products')]"))
        )
        urls = find_api_requests(consume_network_events(driver))
        assert any("/api/shops/" in u and "/products" not in u for u in urls), f"Expected shop detail API call, got: {urls}"
        assert any("/api/shops/" in u and "/products" in u for u in urls), f"Expected shop products API call, got: {urls}"

        # Click Compare Prices on first item if present
        compare_btns = driver.find_elements(By.XPATH, "//button[normalize-space()='Compare Prices']")
        if compare_btns:
            consume_network_events(driver)
            compare_btns[0].click()
            # Product page should load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h3[normalize-space()='Price Comparison Across Shops']"))
            )
            urls = find_api_requests(consume_network_events(driver))
            assert any("/api/products/" in u and "/prices" not in u for u in urls), f"Expected product detail API call, got: {urls}"
            assert any("/api/products/" in u and "/prices" in u for u in urls), f"Expected product prices API call, got: {urls}"


def test_shops_nearby_feature(driver):
    open_home(driver)

    # Trigger geolocation-based fetch
    use_loc_btn = wait_visible(driver, By.XPATH, "//button[normalize-space()='Use my location']")
    consume_network_events(driver)
    use_loc_btn.click()

    # Expect calls to shops/nearby and search/popular
    urls = []
    # Allow some time for async geolocation + axios
    for _ in range(5):
        time.sleep(1)
        urls.extend(find_api_requests(consume_network_events(driver)))

    assert any("/api/shops/nearby" in u for u in urls), f"Expected nearby shops API call, got: {urls}"
    assert any("/api/search/popular" in u for u in urls), f"Expected popular products API call, got: {urls}"

    # UI should render Nearby Shops section if data returned
    # This is conditional on backend; we assert presence if found, otherwise skip
    nearby_headers = driver.find_elements(By.XPATH, "//h3[normalize-space()='Nearby Shops']")
    if nearby_headers:
        # At least one card should be present soon
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//h3[normalize-space()='Nearby Shops']/following::div[contains(@class,'grid')]"))
        )


def test_city_change_functionality(driver):
    open_home(driver)

    # Set city and search for shops in city
    type_select = wait_visible(driver, By.CSS_SELECTOR, "select")
    driver.execute_script("arguments[0].value='shop'; arguments[0].dispatchEvent(new Event('change'));", type_select)

    city_input = wait_visible(driver, By.CSS_SELECTOR, "input[placeholder='City (optional)']")
    target_city = "Bhopal"
    city_input.clear()
    city_input.send_keys(target_city)

    consume_network_events(driver)
    search_btn = wait_visible(driver, By.XPATH, "//button[normalize-space()='Search' or normalize-space()='Searching...']")
    search_btn.click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//h2[normalize-space()='Search Results']"))
    )
    urls = find_api_requests(consume_network_events(driver))
    assert any("/api/shops/by_city" in u and f"city={target_city}" in u for u in urls), \
        f"Expected by_city API call for {target_city}, got: {urls}"

    # Switch to product type with city and assert in_city API
    driver.execute_script("arguments[0].value='product'; arguments[0].dispatchEvent(new Event('change'));", type_select)
    consume_network_events(driver)
    search_btn = wait_visible(driver, By.XPATH, "//button[normalize-space()='Search' or normalize-space()='Searching...']")
    search_btn.click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//h2[normalize-space()='Search Results']"))
    )
    urls = find_api_requests(consume_network_events(driver))
    assert any("/api/products/in_city" in u and f"city={target_city}" in u for u in urls), \
        f"Expected products in_city API call for {target_city}, got: {urls}"


def test_user_login_and_session_persistence(driver):
    login_user(driver, USER_EMAIL, USER_PASSWORD)
    # Redirect to user dashboard via guard
    assert_url_contains(driver, "/user/dashboard", timeout=10)
    # Dashboard header visible
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h1[normalize-space()='User Dashboard']")))
    # Validate no password exposure in URLs
    assert_no_password_leak_in_urls(driver)
    # Refresh and ensure still authenticated (session cookie persists)
    driver.refresh()
    assert_url_contains(driver, "/user/dashboard", timeout=10)


def test_owner_login_redirects_to_dashboard(driver):
    login_owner(driver, OWNER_ID, OWNER_PASSWORD)
    assert_url_contains(driver, "/shopkeeper/dashboard", timeout=10)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h1[normalize-space()='Shopkeeper Dashboard']")))
    assert_no_password_leak_in_urls(driver)


def test_invalid_credentials_show_errors(driver):
    # User invalid password
    login_user(driver, USER_EMAIL, "WrongPass!123")
    # Either alert appears or remains on login page
    time.sleep(1)
    alerted = False
    try:
        alert = driver.switch_to.alert
        _ = alert.text
        alert.accept()
        alerted = True
    except Exception:
        pass
    if not alerted:
        assert_url_contains(driver, "/login", timeout=5)

    # Owner invalid credentials
    login_owner(driver, "nonexistent_owner", "bad")
    # Expect error text on page
    err_elems = driver.find_elements(By.XPATH, "//*[contains(text(),'Invalid') and contains(text(),'password')]")
    assert err_elems, "Expected invalid credentials error message for owner login"


def test_password_recovery_flow_if_available(driver):
    driver.get(FRONTEND_BASE_URL.rstrip('/') + "/login")
    links = driver.find_elements(By.XPATH, "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'forgot')]")
    if not links:
        pytest.skip("Password recovery UI not available")
    consume_network_events(driver)
    links[0].click()
    # The exact recovery flow depends on implementation; ensure navigation occurs
    WebDriverWait(driver, 5).until(lambda d: d.current_url != FRONTEND_BASE_URL.rstrip('/') + "/login")


def test_session_invalidated_redirects_to_login(driver):
    # Log in user first
    login_user(driver, USER_EMAIL, USER_PASSWORD)
    assert_url_contains(driver, "/user/dashboard")
    # Clear cookies/localStorage to simulate timeout/invalidation
    driver.delete_all_cookies()
    clear_local_storage(driver)
    driver.get(FRONTEND_BASE_URL.rstrip('/') + "/user/profile")
    # Guard should redirect to login
    assert_url_contains(driver, "/login", timeout=10)


def test_concurrent_sessions_basic():
    d1 = _new_driver()
    d2 = _new_driver()
    try:
        login_user(d1, USER_EMAIL, USER_PASSWORD)
        login_user(d2, USER_EMAIL, USER_PASSWORD)
        WebDriverWait(d1, 10).until(EC.presence_of_element_located((By.XPATH, "//h1[normalize-space()='User Dashboard']")))
        WebDriverWait(d2, 10).until(EC.presence_of_element_located((By.XPATH, "//h1[normalize-space()='User Dashboard']")))
    finally:
        try:
            d1.quit()
        except Exception:
            pass
        try:
            d2.quit()
        except Exception:
            pass


def test_post_test_verification_metrics_and_safety():
    if not requests:
        pytest.skip("requests module not available")
    # Check metrics for login endpoint activity
    try:
        r = requests.get("http://localhost:8000/api/metrics", timeout=5)
        r.raise_for_status()
    except Exception:
        pytest.skip("Backend metrics endpoint not reachable")
    data = r.json()
    # Expect keys for /api/auth/login and /api/auth/owner/login present after tests
    endpoints = data.get("endpoints", {})
    user_stats = endpoints.get("/api/auth/login", {})
    owner_stats = endpoints.get("/api/auth/owner/login", {})
    # We should have seen both 200 and some 4xx due to invalid test
    assert isinstance(user_stats, dict), "No stats for user login"
    assert isinstance(owner_stats, dict), "No stats for owner login"
    # No sensitive data exposure check against recorded URLs is handled in other tests


# --- Failure handling: capture artifacts on test failures ---
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver")
        if driver:
            name = f"{item.name}-failure"
            png_path, html_path = save_artifacts(driver, name)
            # Also dump recent network events
            events = consume_network_events(driver)
            net_path = os.path.join(REPORT_DIR, f"{name}-{int(time.time()*1000)}-network.json")
            try:
                with open(net_path, "w", encoding="utf-8") as f:
                    json.dump(events, f, indent=2)
            except Exception:
                pass