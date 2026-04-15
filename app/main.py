# app/main.py  — Expts 1-4: FastAPI · JWT · Pydantic · Logging · Metrics
from __future__ import annotations

import os
import time
from datetime import datetime, timedelta
from typing import Annotated

import joblib
import numpy as np

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator

load_dotenv()
_model = joblib.load("model.pkl")
_mlb   = joblib.load("mlb.pkl")

# ── Config ────────────────────────────────────────────────────────────────────
SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ── Logging (Expt 1) ──────────────────────────────────────────────────────────
logger.add("logs/app.log", rotation="10 MB", retention="14 days", level="INFO")

# ── App bootstrap ─────────────────────────────────────────────────────────────
app = FastAPI(title="MedQA MLOps API", version="1.0.0")
Instrumentator().instrument(app).expose(app)          # /metrics endpoint

# ── Auth helpers (Expt 2) ─────────────────────────────────────────────────────
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def _hash_password(password: str) -> str:
    """Truncate to 72 bytes before hashing — bcrypt hard limit."""
    return pwd_ctx.hash(password[:72])


# Stub user store – replace with DB in prod
# Password: admin123  (pre-hashed to avoid startup errors)
USERS_DB: dict[str, dict] = {
    "admin": {
        "username": "admin",
        "hashed_password": _hash_password("admin123"),
        "role": "admin",
    }
}


def _verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain[:72], hashed)


def _create_token(data: dict, expires_delta: timedelta) -> str:
    payload = data | {"exp": datetime.utcnow() + expires_delta}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None or username not in USERS_DB:
            raise exc
    except JWTError:
        raise exc
    return USERS_DB[username]


# ── Pydantic schemas (Expt 3) ─────────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PredictRequest(BaseModel):
    patient_id: str = Field(..., min_length=1)
    symptoms: list[str] = Field(..., min_items=1)
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., pattern="^(M|F|Other)$")


class PredictResponse(BaseModel):
    patient_id: str
    diagnosis: str
    confidence: float
    latency_ms: float


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float


# ── Startup timer ─────────────────────────────────────────────────────────────
_START = time.time()


# ── Routes ────────────────────────────────────────────────────────────────────

# Expt 1 — Health check
@app.get("/health", response_model=HealthResponse, tags=["System"])
def health():
    return {"status": "ok", "uptime_seconds": round(time.time() - _START, 2)}


# Expt 2 — JWT Auth
@app.post("/auth/token", response_model=Token, tags=["Auth"])
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = USERS_DB.get(form.username)
    if not user or not _verify_password(form.password, user["hashed_password"]):
        logger.warning(f"Failed login attempt: {form.username}")
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = _create_token(
        {"sub": user["username"], "role": user["role"]},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    logger.info(f"Token issued for {form.username}")
    return {"access_token": token}


# Expt 3 — Pydantic-validated prediction endpoint
@app.post("/predict", response_model=PredictResponse, tags=["ML"])
def predict(
    req: PredictRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    t0 = time.perf_counter()
    logger.info(f"Predict called by {current_user['username']} for patient {req.patient_id}")

    # ── Real ML model inference ───────────────────────────────────────────────

    symptoms_vec = _mlb.transform([req.symptoms])
    diagnosis    = _model.predict(symptoms_vec)[0]
    proba        = _model.predict_proba(symptoms_vec)[0]
    confidence   = round(float(np.max(proba)), 2)
    # ─────────────────────────────────────────────────────────────────────────

    latency = round((time.perf_counter() - t0) * 1000, 2)
    logger.info(f"Prediction: {diagnosis} ({confidence}) in {latency}ms")
    return PredictResponse(
        patient_id=req.patient_id,
        diagnosis=diagnosis,
        confidence=confidence,
        latency_ms=latency,
    )


# Expt 4 — Admin-only audit log endpoint
@app.get("/admin/logs", tags=["Admin"])
def get_logs(current_user: Annotated[dict, Depends(get_current_user)]):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    try:
        with open("logs/app.log") as f:
            lines = f.readlines()[-100:]
        return {"lines": lines}
    except FileNotFoundError:
        return {"lines": []}