"""API local do protótipo EV ChargeOps — executável com uvicorn."""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.services import build_invoices, dashboard, demand_prediction, detect_anomalies

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
app = FastAPI(title="EV ChargeOps API", version="1.0.0")

class SessionInput(BaseModel):
    rfid_id: str = Field(..., examples=["RFID-1001"])
    inicio: datetime
    fim: datetime
    energia_kwh: float = Field(gt=0)
    potencia_media_kw: float = Field(gt=0)
    status: str = "completed"
    fonte_dados: str = "manual"

def read(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))

def write(name: str, value):
    (DATA / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")

@app.get("/api/health")
def health(): return {"status": "ok", "modo": "simulado"}

@app.get("/api/dashboard")
def get_dashboard(): return dashboard(read("usuarios.json"), read("sessoes.json"), read("configuracoes.json"))

@app.get("/api/sessoes")
def get_sessions(): return read("sessoes.json")

@app.post("/api/sessoes", status_code=201)
def create_session(item: SessionInput):
    users, sessions = read("usuarios.json"), read("sessoes.json")
    user = next((u for u in users if u["rfid_id"] == item.rfid_id and u["ativo"]), None)
    if not user: raise HTTPException(status_code=404, detail="RFID não autorizado")
    if item.fim <= item.inicio: raise HTTPException(status_code=422, detail="Fim deve ser posterior ao início")
    session = {"id": f"ses-{uuid.uuid4().hex[:8]}", "usuario_id": user["id"], **item.model_dump(mode="json")}
    sessions.append(session); write("sessoes.json", sessions)
    return {"mensagem": "Sessão registrada", "sessao": session}

@app.get("/api/faturas")
def invoices(): return build_invoices(read("usuarios.json"), read("sessoes.json"), read("configuracoes.json"))

@app.get("/api/ia/previsao-demanda")
def prediction(): return demand_prediction(read("sessoes.json"))

@app.get("/api/ia/anomalias")
def anomalies(): return detect_anomalies(read("sessoes.json"))

app.mount("/", StaticFiles(directory=ROOT / "static", html=True), name="static")
