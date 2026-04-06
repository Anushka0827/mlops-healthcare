# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _get_token() -> str:
    r = client.post("/auth/token", data={"username": "admin", "password": "admin123"})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_login_success():
    token = _get_token()
    assert len(token) > 10


def test_login_fail():
    r = client.post("/auth/token", data={"username": "admin", "password": "wrong"})
    assert r.status_code == 400


def test_predict_authenticated():
    token = _get_token()
    payload = {"patient_id": "P-001", "symptoms": ["cough", "fever"], "age": 40, "gender": "M"}
    r = client.post("/predict", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["diagnosis"] == "Pneumonia"


def test_predict_unauthenticated():
    payload = {"patient_id": "P-002", "symptoms": ["headache"], "age": 30, "gender": "F"}
    r = client.post("/predict", json=payload)
    assert r.status_code == 401