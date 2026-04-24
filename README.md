# 🏥 MedQA MLOps: Patient Triage System

**A production-ready Machine Learning Operations (MLOps) pipeline for clinical patient triage.**

This repository contains a complete end-to-end Machine Learning pipeline. It trains a clinical symptom-checker model (Random Forest), serves the inference via a secure and structured **FastAPI** backend, and visualizes predictions through a dynamic **Streamlit** UI. The entire system is containerized via **Docker** and automated using **GitHub Actions**.

---

## 🧪 Course Structure & Experiments Completed
This project implements the following MLOps architectures:

- [x] **Expt 1:** Train ML model and sync to Cloud Object Storage (AWS S3 Artifact Registry)
- [x] **Expt 2:** Create backend for model inference (FastAPI, Pydantic schemas)
- [x] **Expt 3:** Error handling and logging (Loguru, structured logging)
- [x] **Expt 4:** Implement basic authentication (JWT-based token auth)
- [x] **Expt 5:** Create container for the FastAPI ML service (Dockerfile)
- [x] **Expt 6:** Verify and test API (Pytest, Postman Auth/Validation testing)
- [x] **Expt 7:** Set up CI/CD pipeline (GitHub Actions for Lint/Test/Build)
- [x] **Expt 8:** Deploy Docker container to Cloud VM (AWS EC2 / Docker Compose)
- [x] **Expt 9:** Create frontend to visualize predictions using test data (Streamlit)
- [x] **Expt 10:** Create frontend with real-time user input (Professional Monitoring UI)
- [x] **Expt 11:** Model monitoring using Prometheus & Grafana
- [ ] **Expt 12:** Kubernetes setup for ML application *(Next Phase)*

---

## 🚀 Step-by-Step Execution Guide

You can run this project locally, either using standard Python or via Docker Compose. 

### Method 1: Local Python Environment
**1. Environment Setup**
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

**2. Train the Machine Learning Model (Expt 1)**
Generates the necessary `model.pkl` and `mlb.pkl` artifacts.
```bash
python train_model.py
```

**3. Run Automated Tests (Expt 6)**
```bash
pytest tests/ -v
```

**4. Start the FastAPI Backend (Expt 2, 3, 4)**
```bash
uvicorn app.main:app --reload
```
*Navigate to `http://localhost:8000/docs` to test the secure API Swagger interface.*

**5. Start the Streamlit Frontend (Expt 9, 10)**
*(In a new terminal window)*
```bash
streamlit run ui/app.py
```
*Navigate to `http://localhost:8501` to view the patient dashboard. Log in using `admin` / `admin123`.*

---

### Method 2: One-Click Docker Orchestration (Expt 5 & 8)
To run the entire system (both backend and frontend) via Docker containers, connected via an internal bridge network:

```bash
docker compose up --build -d
```
- **Backend API:** Accessible at `http://localhost:8000/docs`
- **Frontend UI:** Accessible at `http://localhost:8501`
- **Prometheus Metrics:** Accessible at `http://localhost:9090`
- **Grafana Dashboards:** Accessible at `http://localhost:3000` (Default Login: `admin` / `admin`)

*(To stop the containers, run `docker compose down`)*

---

## 🔐 Available API Endpoints
All API endpoints are strictly validated using Pydantic.

| Method | Endpoint | Description | Auth Required? |
|--------|---------|-------------|----------------|
| `GET`  | `/health` | Application status and uptime | No |
| `POST` | `/auth/token` | Generates a JWT access token | No |
| `POST` | `/predict` | Predicts diagnosis based on symptoms | Yes (Bearer) |
| `GET`  | `/admin/logs` | Fetches the latest system logs | Yes (Admin) |

