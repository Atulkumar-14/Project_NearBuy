from locust import HttpUser, task, between


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Attempt login with seeded demo user
        payload = {
            "email": "user.demo@example.com",
            "password": "Password@123",
        }
        with self.client.post("/api/auth/login", json=payload, name="auth_login", catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"login failed: {resp.status_code} {resp.text}")
            else:
                # Extract token to use in headers
                try:
                    tok = resp.json().get("access_token")
                    self.headers = {"Authorization": f"Bearer {tok}"}
                except Exception:
                    self.headers = {}

    @task(3)
    def list_users(self):
        self.client.get("/api/users", name="users_list")

    @task(2)
    def get_me(self):
        self.client.get("/api/users/me", headers=getattr(self, "headers", {}), name="users_me")