# ui/app.py — Expt 9: Streamlit frontend
from __future__ import annotations

import os
import requests
import streamlit as st
import plotly.graph_objects as go

API = os.getenv("API_URL", "http://localhost:8000")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MedQA MLOps Dashboard",
    page_icon="🏥",
    layout="wide",
)

# ── Session state ─────────────────────────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "history" not in st.session_state:
    st.session_state.history: list[dict] = []

# ── Sidebar — Auth ────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🔐 Auth")
    username = st.text_input("Username", value="admin")
    password = st.text_input("Password", type="password", value="admin123")

    if st.button("Login", use_container_width=True):
        r = requests.post(
            f"{API}/auth/token",
            data={"username": username, "password": password},
        )
        if r.status_code == 200:
            st.session_state.token = r.json()["access_token"]
            st.success("Authenticated ✓")
        else:
            st.error(f"Login failed: {r.json().get('detail')}")

    st.divider()
    try:
        health = requests.get(f"{API}/health", timeout=2).json()
        st.metric("API Status", health.get("status", "—").upper())
        st.metric("Uptime (s)", health.get("uptime_seconds", "—"))
    except Exception:
        st.error("⚠️ API Offline — start uvicorn first")

# ── Main — Prediction form ─────────────────────────────────────────────────────
st.title("🏥 MedQA MLOps · Patient Triage")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Patient Input")
    patient_id = st.text_input("Patient ID", placeholder="P-001")
    age = st.slider("Age", 0, 120, 35)
    gender = st.selectbox("Gender", ["M", "F", "Other"])
    symptoms_raw = st.text_area(
        "Symptoms (comma-separated)",
        placeholder="cough, fever, fatigue",
    )

    if st.button("Run Prediction", type="primary", use_container_width=True):
        if not st.session_state.token:
            st.warning("Login first.")
        else:
            payload = {
                "patient_id": patient_id,
                "symptoms": [s.strip() for s in symptoms_raw.split(",") if s.strip()],
                "age": age,
                "gender": gender,
            }
            r = requests.post(
                f"{API}/predict",
                json=payload,
                headers={"Authorization": f"Bearer {st.session_state.token}"},
            )
            if r.status_code == 200:
                result = r.json()
                st.session_state.history.append(result)
                st.success(f"Diagnosis: **{result['diagnosis']}**  |  Confidence: {result['confidence']:.0%}  |  {result['latency_ms']} ms")
            else:
                st.error(r.json().get("detail", "Error"))

with col2:
    st.subheader("Prediction History")
    if st.session_state.history:
        diagnoses = [h["diagnosis"] for h in st.session_state.history]
        confs = [h["confidence"] for h in st.session_state.history]
        ids = [h["patient_id"] for h in st.session_state.history]

        fig = go.Figure(
            go.Bar(
                x=ids,
                y=confs,
                text=[f"{c:.0%}" for c in confs],
                textposition="outside",
                marker_color=[
                    "#16a34a" if d == "Pneumonia" else "#2563eb"
                    for d in diagnoses
                ],
            )
        )
        fig.update_layout(
            yaxis=dict(range=[0, 1.1], tickformat=".0%", title="Confidence"),
            xaxis_title="Patient ID",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=10),
            height=320,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            [
                {"ID": h["patient_id"], "Diagnosis": h["diagnosis"],
                 "Confidence": f"{h['confidence']:.0%}", "Latency (ms)": h["latency_ms"]}
                for h in st.session_state.history
            ],
            use_container_width=True,
        )
    else:
        st.info("No predictions yet. Submit a patient above.")