#application run in desktop


import os
import json
import threading
from flask import Flask, jsonify, request, render_template

from services.parser import organize
from services.storage import save, exists
from services.email_service import send_email
from services.collect import coletar_licitacoes_reais, enriquecer_com_itens
from scheduler import (
    iniciar_scheduler,
    reagendar,
    salvar_config,
    carregar_config,
    executar_agora_async,
    proximo_agendamento,
)

app = Flask(__name__, template_folder="views")


# ─── Healthcheck (Electron aguarda isso antes de abrir a janela) ──────────────
@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# ─── Página principal ─────────────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")


# ─── Coleta manual via painel ─────────────────────────────────────────────────
@app.route("/licitacoes", methods=["POST"])
def coletar_licitacoes():
    data = request.get_json() or {}

    config = carregar_config()

    max_paginas   = data.get("max_paginas",   config.get("max_paginas", 5))
    tamanho       = data.get("tamanho",        config.get("tamanho", 10))
    palavras_chave= data.get("palavras_chave", config.get("palavras_chave"))
    number_days   = data.get("number_days",    config.get("number_days", 7))
    prompt        = data.get("prompt",         config.get("prompt", ""))

    editais = coletar_licitacoes_reais(
        max_paginas=max_paginas,
        tamanho=tamanho,
        palavras_chave=palavras_chave,
        number_days=number_days,
        prompt=prompt,
    )
    editais_com_itens = enriquecer_com_itens(editais)
    dados = organize(editais_com_itens)

    novos = [d for d in dados if not exists(d["id"])]
    for item in novos:
        save(item)

    send_email(novos)
    return jsonify(dados)


# ─── Executar agora (disparo imediato assíncrono) ─────────────────────────────
@app.route("/executar-agora", methods=["POST"])
def executar_agora():
    executar_agora_async()
    prox = proximo_agendamento()
    return jsonify({
        "ok": True,
        "msg": "Coleta iniciada em segundo plano.",
        "proximo": prox,
    })


# ─── Configuração do agendador ────────────────────────────────────────────────
@app.route("/config", methods=["GET"])
def get_config():
    return jsonify(carregar_config())


@app.route("/config", methods=["POST"])
def set_config():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON inválido"}), 400

    config = salvar_config(data)

    # Atualiza o scheduler em tempo real
    reagendar(config.get("horario", "08:00"), ativo=config.get("ativo", True))

    prox = proximo_agendamento()
    return jsonify({"ok": True, "config": config, "proximo": prox})


# ─── Status do agendador ──────────────────────────────────────────────────────
@app.route("/status")
def status():
    config = carregar_config()
    prox = proximo_agendamento()
    return jsonify({
        "agendado": config.get("ativo", True),
        "horario": config.get("horario", "08:00"),
        "proximo_disparo": prox,
    })


# ─── Boot ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    iniciar_scheduler()          # Sobe o APScheduler em background
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)