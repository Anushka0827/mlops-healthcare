# tests/test_api.py — pytest test suite for MedQA MLOps API
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_token(username="admin", password="admin123") -> str:
    r = client.post("/auth/token", data={"username": username, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def auth_headers() -> dict:
    return {"Authorization": f"Bearer {get_token()}"}


# ── Health check ──────────────────────────────────────────────────────────────
def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "uptime_seconds" in data


# ── Auth ──────────────────────────────────────────────────────────────────────
def test_login_success():
    r = client.post("/auth/token", data={"username": "admin", "password": "admin123"})
    assert r.status_code == 200
    assert "access_token" in r.json()
    assert r.json()["token_type"] == "bearer"


def test_login_wrong_password():
    r = client.post("/auth/token", data={"username": "admin", "password": "wrongpass"})
    assert r.status_code == 400


def test_login_unknown_user():
    r = client.post("/auth/token", data={"username": "ghost", "password": "x"})
    assert r.status_code == 400


# ── Predict ───────────────────────────────────────────────────────────────────
def test_predict_pneumonia():
    payload = {
        "patient_id": "P-001",
        "symptoms": ["cough", "fever"],
        "age": 40,
        "gender": "M",
    }
    r = client.post("/predict", json=payload, headers=auth_headers())
    assert r.status_code == 200
    data = r.json()
    assert data["patient_id"] == "P-001"
    assert data["diagnosis"] == "Pneumonia"
    assert 0.70 <= data["confidence"] <= 0.95  # Confidence range
    assert "latency_ms" in data


def test_predict_general_checkup():
    payload = {
        "patient_id": "P-002",
        "symptoms": ["headache"],
        "age": 25,
        "gender": "F",
    }
    r = client.post("/predict", json=payload, headers=auth_headers())
    assert r.status_code == 200
    assert r.json()["diagnosis"] == "General Checkup"


def test_predict_unauthenticated():
    payload = {
        "patient_id": "P-003",
        "symptoms": ["cough"],
        "age": 30,
        "gender": "M",
    }
    r = client.post("/predict", json=payload)
    assert r.status_code == 401


def test_predict_invalid_gender():
    payload = {
        "patient_id": "P-004",
        "symptoms": ["cough"],
        "age": 30,
        "gender": "X",  # invalid
    }
    r = client.post("/predict", json=payload, headers=auth_headers())
    assert r.status_code == 422


def test_predict_invalid_age():
    payload = {
        "patient_id": "P-005",
        "symptoms": ["cough"],
        "age": 200,  # out of range
        "gender": "M",
    }
    r = client.post("/predict", json=payload, headers=auth_headers())
    assert r.status_code == 422


# ── Admin logs ────────────────────────────────────────────────────────────────
def test_admin_logs_success():
    r = client.get("/admin/logs", headers=auth_headers())
    assert r.status_code == 200
    assert "lines" in r.json()


def test_admin_logs_unauthenticated():
    r = client.get("/admin/logs")
    assert r.status_code == 401