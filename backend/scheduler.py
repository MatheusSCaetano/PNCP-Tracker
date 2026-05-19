import json
import os
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Importado no app.py que inicia tudo
sched = BackgroundScheduler(timezone="America/Sao_Paulo")
_lock = threading.Lock()

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
DEFAULT_CONFIG = {
    "horario": "08:00",
    "ativo": True,
    "prompt": "",
    "palavras_chave": "software juridico",
    "number_days": 7,
    "max_paginas": 5,
    "tamanho": 10,
}


def carregar_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULT_CONFIG, **data}
        except Exception as e:
            print("[scheduler] Erro ao ler config:", e)
    return DEFAULT_CONFIG.copy()


def salvar_config(config: dict):
    merged = {**DEFAULT_CONFIG, **config}
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    return merged


def _executar_coleta():
    """Função que roda no horário agendado."""
    from services.collect import coletar_licitacoes_reais, enriquecer_com_itens
    from services.parser import organize
    from services.storage import save, exists
    from services.email_service import send_email

    config = carregar_config()
    print(f"[scheduler] Iniciando coleta automática — {config['horario']}")

    try:
        editais = coletar_licitacoes_reais(
            max_paginas=config.get("max_paginas", 5),
            tamanho=config.get("tamanho", 10),
            palavras_chave=config.get("palavras_chave"),
            number_days=config.get("number_days", 7),
            prompt=config.get("prompt", ""),
        )
        editais_com_itens = enriquecer_com_itens(editais)
        dados = organize(editais_com_itens)

        novos = [d for d in dados if not exists(d["id"])]
        for item in novos:
            save(item)

        if novos:
            send_email(novos)
            print(f"[scheduler] {len(novos)} nova(s) licitação(ões) enviada(s) por email.")
        else:
            print("[scheduler] Nenhuma licitação nova encontrada.")

    except Exception as e:
        print("[scheduler] Erro durante coleta:", e)


def _parse_horario(horario_str: str):
    """Converte '08:30' em (hora=8, minuto=30)."""
    try:
        h, m = horario_str.strip().split(":")
        return int(h), int(m)
    except Exception:
        return 8, 0


def iniciar_scheduler():
    """Inicia o APScheduler com o horário salvo em config.json."""
    config = carregar_config()
    hora, minuto = _parse_horario(config.get("horario", "08:00"))

    if sched.running:
        return

    if config.get("ativo", True):
        sched.add_job(
            _executar_coleta,
            CronTrigger(hour=hora, minute=minuto, timezone="America/Sao_Paulo"),
            id="coleta_diaria",
            replace_existing=True,
        )
        print(f"[scheduler] Agendado para rodar todo dia às {config['horario']}")

    sched.start()
    print("[scheduler] Scheduler iniciado.")


def reagendar(horario_str: str, ativo: bool = True):
    """Atualiza o horário do job em tempo real, sem reiniciar."""
    with _lock:
        hora, minuto = _parse_horario(horario_str)

        if sched.get_job("coleta_diaria"):
            sched.remove_job("coleta_diaria")

        if ativo:
            sched.add_job(
                _executar_coleta,
                CronTrigger(hour=hora, minute=minuto, timezone="America/Sao_Paulo"),
                id="coleta_diaria",
                replace_existing=True,
            )
            print(f"[scheduler] Reagendado para {horario_str}")
        else:
            print("[scheduler] Agendamento desativado.")


def executar_agora_async():
    """Dispara a coleta imediatamente em thread separada."""
    t = threading.Thread(target=_executar_coleta, daemon=True)
    t.start()
    return t


def proximo_agendamento() -> str | None:
    """Retorna a data/hora do próximo disparo como string ISO."""
    job = sched.get_job("coleta_diaria")
    if job and job.next_run_time:
        return job.next_run_time.isoformat()
    return None