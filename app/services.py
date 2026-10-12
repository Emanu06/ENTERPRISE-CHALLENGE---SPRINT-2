"""Regras de negócio do EV ChargeOps: rateio, previsão e anomalias."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression


def completed_sessions(sessions: list[dict]) -> list[dict]:
    return [s for s in sessions if s["status"] == "completed"]


def build_invoices(users: list[dict], sessions: list[dict], config: dict) -> list[dict]:
    """Aplica a fórmula aprovada na Sprint 01 para o período configurado."""
    period = config["periodo"]
    totals: dict[str, float] = defaultdict(float)
    for session in completed_sessions(sessions):
        if session["inicio"].startswith(period):
            totals[session["usuario_id"]] += session["energia_kwh"]
    active = [user for user in users if totals[user["id"]] > 0]
    share = config["custo_infraestrutura"] / len(active) if active else 0
    return [{
        "usuario_id": user["id"], "usuario": user["nome"], "unidade": user["unidade"],
        "energia_total_kwh": round(totals[user["id"]], 3), "tarifa_kwh": config["tarifa_kwh"],
        "custo_energia": round(totals[user["id"]] * config["tarifa_kwh"], 2),
        "custo_infraestrutura": round(share if user in active else 0, 2),
        "total": round(totals[user["id"]] * config["tarifa_kwh"] + (share if user in active else 0), 2),
    } for user in users]


def demand_prediction(sessions: list[dict]) -> list[dict]:
    """Regressão linear por hora e dia da semana; saída é estimativa de kWh."""
    valid = completed_sessions(sessions)
    if len(valid) < 3:
        return []
    x, y = [], []
    for session in valid:
        start = datetime.fromisoformat(session["inicio"])
        x.append([start.weekday(), start.hour])
        y.append(session["energia_kwh"])
    model = LinearRegression().fit(x, y)
    result = []
    # Próximas faixas ilustrativas: segunda-feira, horários de maior uso observados.
    for hour in (8, 12, 18, 20):
        prediction = max(0, float(model.predict([[0, hour]])[0]))
        level = "alto" if prediction >= 12 else "moderado" if prediction >= 8 else "baixo"
        result.append({"faixa": f"{hour:02d}:00–{hour + 1:02d}:00", "kwh_estimado": round(prediction, 2), "nivel": level})
    return result


def detect_anomalies(sessions: list[dict]) -> list[dict]:
    """Isolation Forest sinaliza desvios de energia, duração e potência média."""
    if len(sessions) < 5:
        return []
    features = []
    for session in sessions:
        start, end = datetime.fromisoformat(session["inicio"]), datetime.fromisoformat(session["fim"])
        duration = (end - start).total_seconds() / 60
        features.append([session["energia_kwh"], duration, session["potencia_media_kw"]])
    detector = IsolationForest(contamination=0.15, random_state=42).fit(np.array(features))
    flags = detector.predict(np.array(features))
    return [{
        "sessao_id": session["id"], "usuario_id": session["usuario_id"], "energia_kwh": session["energia_kwh"],
        "status": session["status"], "motivo": "Padrão de consumo/duração/potência fora do perfil esperado"
    } for session, flag in zip(sessions, flags) if flag == -1 or session["status"] == "interrupted"]


def dashboard(users: list[dict], sessions: list[dict], config: dict) -> dict[str, Any]:
    invoices = build_invoices(users, sessions, config)
    completed = completed_sessions(sessions)
    return {
        "periodo": config["periodo"], "carregador": config["carregador"], "sessoes": len(sessions),
        "energia_total_kwh": round(sum(s["energia_kwh"] for s in completed), 2),
        "usuarios_ativos": len([i for i in invoices if i["energia_total_kwh"] > 0]),
        "receita_estimada": round(sum(i["total"] for i in invoices), 2),
        "interrompidas": len([s for s in sessions if s["status"] == "interrupted"]),
    }
