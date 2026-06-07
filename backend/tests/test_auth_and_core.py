"""Backend API tests for Investigation Portal - auth, /me, categories, users"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://field-ops-44.preview.emergentagent.com").rstrip("/")
ORIGIN = BASE_URL

ADMIN = {"email": "admin@investigationportal.com", "password": "Admin@123"}
INVESTIGATOR = {"email": "investigator@test.com", "password": "Investigator@123"}


@pytest.fixture
def admin_session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json", "Origin": ORIGIN})
    r = s.post(f"{BASE_URL}/api/auth/login", json=ADMIN)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    return s


# --- Auth ---
class TestAuth:
    def test_login_admin_success(self):
        r = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN, headers={"Origin": ORIGIN})
        assert r.status_code == 200
        data = r.json()
        assert data["email"] == ADMIN["email"]
        assert data["role"] == "admin"
        # cookies should be set
        cookie_names = {c.name for c in r.cookies}
        assert "access_token" in cookie_names
        assert "refresh_token" in cookie_names

    def test_login_invalid_credentials(self):
        r = requests.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN["email"], "password": "wrong"}, headers={"Origin": ORIGIN})
        assert r.status_code == 401

    def test_me_with_cookie(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/auth/me")
        assert r.status_code == 200
        data = r.json()
        assert data["email"] == ADMIN["email"]
        assert data["role"] == "admin"

    def test_me_without_cookie(self):
        r = requests.get(f"{BASE_URL}/api/auth/me", headers={"Origin": ORIGIN})
        assert r.status_code == 401

    def test_login_investigator(self):
        r = requests.post(f"{BASE_URL}/api/auth/login", json=INVESTIGATOR, headers={"Origin": ORIGIN})
        # Investigator may or may not be seeded
        assert r.status_code in (200, 401)

    def test_logout(self, admin_session):
        r = admin_session.post(f"{BASE_URL}/api/auth/logout")
        assert r.status_code == 200

    def test_cors_credentials_origin_not_wildcard(self):
        """CORS with credentials must NOT use Allow-Origin: * - browsers reject this."""
        r = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN, headers={"Origin": ORIGIN})
        allow_origin = r.headers.get("access-control-allow-origin", "")
        allow_creds = r.headers.get("access-control-allow-credentials", "")
        # Note: this asserts proper CORS - will fail if proxy adds *
        if allow_creds.lower() == "true":
            assert allow_origin != "*", (
                f"CRITICAL CORS BUG: Allow-Origin='*' with Allow-Credentials=true is invalid per CORS spec. "
                f"Browsers will reject cookies. Got: origin={allow_origin}"
            )


# --- Categories (pre-seeded) ---
class TestCategories:
    def test_list_categories_unauthed(self):
        r = requests.get(f"{BASE_URL}/api/categories", headers={"Origin": ORIGIN})
        # categories endpoint might be public or protected; check both
        assert r.status_code in (200, 401)

    def test_list_categories_authed(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/categories")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Categories should be pre-seeded"
        # Validate shape - no _id leaked
        for c in data:
            assert "id" in c
            assert "name" in c
            assert "_id" not in c

    def test_list_subcategories(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/sub-categories")
        assert r.status_code in (200, 404)

    def test_list_service_categories(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/service-categories")
        assert r.status_code in (200, 404)


# --- Users (admin only) ---
class TestUsers:
    def test_list_users_as_admin(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/users")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert any(u["email"] == ADMIN["email"] for u in data)
        for u in data:
            assert "id" in u
            assert "_id" not in u
            assert "password_hash" not in u

    def test_list_users_unauthed(self):
        r = requests.get(f"{BASE_URL}/api/users", headers={"Origin": ORIGIN})
        assert r.status_code == 401


# --- Investigations ---
class TestInvestigations:
    def test_list_investigations(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/investigations")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
