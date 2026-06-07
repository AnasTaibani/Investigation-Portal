"""Findings submission workflow E2E backend tests."""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://field-ops-44.preview.emergentagent.com').rstrip('/')
INV_CREDS = {"email": "investigator@test.com", "password": "Investigator@123"}


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/auth/login", json=INV_CREDS)
    assert r.status_code == 200, f"Login failed: {r.status_code} {r.text}"
    return s


def _find_in_progress(session):
    r = session.get(f"{BASE_URL}/api/investigations?status=in_progress")
    assert r.status_code == 200
    items = r.json()
    # Prefer ones that already have a completed service or evidence so submission is allowed
    for it in items:
        full = session.get(f"{BASE_URL}/api/investigations/{it['investigation_id']}").json()
        services = full.get("services", [])
        if any(s.get("status") == "completed" for s in services):
            return full
    # Otherwise, take first and try to mark a service complete
    if items:
        full = session.get(f"{BASE_URL}/api/investigations/{items[0]['investigation_id']}").json()
        for s in full.get("services", []):
            if s.get("status") == "pending":
                session.put(
                    f"{BASE_URL}/api/investigations/{full['investigation_id']}/services/{s['id']}",
                    json={"status": "completed", "remarks": "TEST_ auto-completed"},
                )
                break
        return session.get(f"{BASE_URL}/api/investigations/{full['investigation_id']}").json()
    return None


def _find_assigned(session):
    r = session.get(f"{BASE_URL}/api/investigations?status=assigned")
    assert r.status_code == 200
    items = r.json()
    return items[0] if items else None


def test_login(session):
    r = session.get(f"{BASE_URL}/api/auth/me")
    assert r.status_code == 200
    assert r.json().get("email") == INV_CREDS["email"]


def test_findings_full_workflow(session):
    """Complete workflow: pick or create in_progress case -> submit findings -> verify."""
    inv = _find_in_progress(session)
    if not inv:
        assigned = _find_assigned(session)
        assert assigned, "No assigned or in_progress investigation available"
        rr = session.put(
            f"{BASE_URL}/api/investigations/{assigned['investigation_id']}/status",
            json={"status": "in_progress"},
        )
        assert rr.status_code in (200, 204), f"start failed {rr.status_code} {rr.text}"
        inv = session.get(f"{BASE_URL}/api/investigations/{assigned['investigation_id']}").json()

    inv_id = inv["investigation_id"]
    assert inv["status"] == "in_progress"

    payload = {
        "observations": "TEST_ Observations recorded during site visit.",
        "conclusion": "TEST_ Findings indicate the claim is genuine.",
        "outcome": "genuine",
        "recommendation": "approve",
    }
    r = session.post(f"{BASE_URL}/api/investigations/{inv_id}/findings", json=payload)
    assert r.status_code in (200, 201), f"submit failed {r.status_code} {r.text}"

    # GET findings - verify persistence
    g = session.get(f"{BASE_URL}/api/investigations/{inv_id}/findings")
    assert g.status_code == 200, f"GET findings failed: {g.status_code} {g.text}"
    fg = g.json()
    assert fg["observations"] == payload["observations"]
    assert fg["conclusion"] == payload["conclusion"]
    assert fg["outcome"] == "genuine"
    assert fg["recommendation"] == "approve"
    assert fg.get("submitted_by_name")
    assert fg.get("submitted_at")

    # Verify status transition
    inv2 = session.get(f"{BASE_URL}/api/investigations/{inv_id}").json()
    assert inv2["status"] == "submitted", f"Expected submitted, got {inv2['status']}"

    # Verify list reflects submitted status
    lst = session.get(f"{BASE_URL}/api/investigations?status=submitted").json()
    assert any(x["investigation_id"] == inv_id for x in lst), "Case missing from submitted list"

    # Verify timeline has findings_submitted event
    acts = session.get(f"{BASE_URL}/api/investigations/{inv_id}/activities").json()
    types = [a.get("activity_type") or a.get("type") for a in acts]
    descriptions = " ".join([str(a.get("description", "")).lower() for a in acts])
    assert "findings_submitted" in types or "findings" in descriptions, \
        f"No findings_submitted event found. Types: {types}"


def test_findings_validation_missing_fields(session):
    """Backend should reject incomplete findings."""
    inv = _find_in_progress(session)
    if not inv:
        pytest.skip("No in_progress case to test validation against")
    r = session.post(
        f"{BASE_URL}/api/investigations/{inv['investigation_id']}/findings",
        json={"observations": "only obs"},
    )
    assert r.status_code in (400, 422), f"Expected validation error, got {r.status_code}"


def test_findings_inv000010_persistence(session):
    """Verify previously-submitted INV000010 findings still persist."""
    r = session.get(f"{BASE_URL}/api/investigations/INV000010")
    if r.status_code != 200:
        pytest.skip("INV000010 not present")
    inv = r.json()
    if inv["status"] != "submitted":
        pytest.skip(f"INV000010 status is {inv['status']}, expected submitted")
    f = session.get(f"{BASE_URL}/api/investigations/INV000010/findings")
    assert f.status_code == 200
    data = f.json()
    assert data.get("observations")
    assert data.get("conclusion")
    assert data.get("outcome")
    assert data.get("recommendation")
