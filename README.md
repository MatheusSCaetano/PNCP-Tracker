# 🏛️ PNCP Tracker

Monitor automatizado de licitações do Portal Nacional de Contratações Públicas (PNCP), com classificação por IA, notificação por e-mail e interface desktop.

---

## Visão geral

O PNCP Tracker coleta editais do PNCP, classifica automaticamente os relevantes para o seu negócio usando IA (Groq/LLaMA), e envia um e-mail com os resultados. Roda como aplicação desktop (Electron + Python Flask) com agendamento diário configurável.

```
Coleta PNCP → Classificação IA → Filtro de relevância → E-mail automático
```

---

## Funcionalidades

- Busca paginada na API pública do PNCP
- Classificação de editais por IA com score de relevância (0–10)
- Filtro por palavras-chave e janela de dias
- Enriquecimento com itens do edital
- Deduplicação via banco SQLite local
- Notificação por e-mail (Gmail SMTP)
- Agendamento diário configurável (ex: todo dia às 08:00)
- Interface desktop com bandeja do sistema (minimiza, não fecha)
- Execução manual pelo painel ou pelo menu da bandeja

---

## Estrutura do projeto

```
PNCP-Tracker/
├── backend/
│   ├── app.py                  # Flask — rotas da API interna
│   ├── scheduler.py            # APScheduler — agendamento diário
│   ├── config.json             # Configurações salvas (gerado automaticamente)
│   ├── database.db             # SQLite — IDs já notificados
│   ├── requirements.txt
│   ├── .env                    # Credenciais (não versionar)
│   └── services/
│       ├── ai_classifier.py    # Classificação via Groq/LLaMA
│       ├── collect.py          # Coleta e enriquecimento de editais
│       ├── email_service.py    # Envio de e-mail via Gmail
│       ├── filter.py           # Filtro por palavras-chave
│       ├── parser.py           # Normalização dos dados
│       └── storage.py          # Persistência SQLite
├── electron/
│   ├── main.js                 # Processo principal Electron
│   ├── preload.js              # Bridge segura renderer ↔ main
│   ├── package.json
│   └── error.html              # Tela de fallback
└── views/
    └── index.html              # Interface do painel
```

---

## Pré-requisitos

- Python 3.11+
- Node.js 18+
- Conta no [Groq](https://console.groq.com) (gratuita) para a chave de API
- Conta Gmail com [senha de app](https://support.google.com/accounts/answer/185833) habilitada

---

## Instalação e execução

### 1. Configurar o `.env`

Crie o arquivo `backend/.env`:

```env
OPENAI_API_KEY=gsk_sua_chave_do_groq_aqui
EMAIL_USER=seu@gmail.com
EMAIL_PASS=sua_senha_de_app_gmail
```

> **Atenção:** use a senha de app do Gmail, não a senha normal da conta.

### 2. Instalar dependências Python

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 3. Instalar dependências Electron

```bash
cd electron
npm install
```

### 4. Rodar em modo desenvolvimento

```bash
# Terminal 1 — backend
cd backend
source venv/bin/activate
python app.py

# Terminal 2 — desktop
cd electron
npm start
```

---

## Gerar o executável

### Empacotar o backend (Python → binário)

```bash
cd backend
source venv/bin/activate
pyinstaller --onefile --name backend app.py
# Gera: backend/dist/backend (Linux/Mac) ou backend/dist/backend.exe (Windows)
```

### Gerar o instalador

```bash
cd electron
npm run dist:linux    # → AppImage
npm run dist:win      # → instalador .exe (NSIS)
npm run dist:mac      # → .dmg
```

O arquivo final fica em `dist-electron/`.

---

## Configuração pelo painel

Acesse a aba **Configurações** na interface para definir:

| Campo | Descrição |
|---|---|
| Horário diário | Hora em que a coleta roda automaticamente |
| Ativo | Liga/desliga o agendamento sem fechar o app |
| Palavras-chave | Termos de busca enviados ao PNCP |
| Máx. páginas | Quantidade de páginas da API a percorrer |
| Janela de dias | Só inclui editais publicados nos últimos N dias |
| Prompt de IA | Instrução que define o perfil de relevância |

As configurações são salvas em `backend/config.json` e aplicadas imediatamente, sem reiniciar.

---

## Como funciona a classificação

Cada edital coletado é enviado ao modelo `llama-3.3-70b-versatile` (via Groq) com o prompt configurado. O modelo retorna:

```json
{
  "score": 8,
  "relevante": true,
  "motivo": "Menciona software jurídico e gestão processual",
  "tecnologias": ["SaaS", "IA jurídica"]
}
```

Editais com `score >= 7` são considerados relevantes e incluídos no e-mail.

---

## Rotas da API interna (Flask)

| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Healthcheck (usado pelo Electron na inicialização) |
| GET | `/` | Painel web |
| POST | `/licitacoes` | Coleta manual com parâmetros customizados |
| POST | `/executar-agora` | Dispara coleta imediata em background |
| GET | `/config` | Retorna configuração atual |
| POST | `/config` | Salva configuração e reagenda |
| GET | `/status` | Status e próximo disparo do agendador |

---

## Comportamento da janela desktop

- Fechar a janela **minimiza para a bandeja** — o app continua rodando e o agendamento funciona normalmente
- O menu da bandeja permite abrir o painel, executar coleta agora ou encerrar o app
- Para encerrar completamente: clique com botão direito na bandeja → **Sair**

---

## Problemas comuns

**Tela preta ao abrir**
O Flask ainda não subiu quando o Electron carregou. Rode primeiro `python app.py` e depois `npm start` para testar. Em produção, aumente o timeout em `main.js`: `waitForFlask(40, 800)`.

**`TemplateNotFound: index.html`**
A pasta `views/` precisa estar dentro de `backend/`. Mova com `mv views/ backend/views/`.

**`SQLite objects created in a thread`**
Certifique-se de estar usando a versão corrigida do `storage.py` que cria uma conexão por chamada.

**Timeout na API do PNCP**
O PNCP pode ser lento em horários de pico. O `collect.py` já usa `timeout=(10, 45)` e pula páginas com erro. Tente novamente ou reduza `max_paginas`.

**Chave Groq inválida**
Gere uma nova chave em [console.groq.com/keys](https://console.groq.com/keys). Verifique que o `.env` não tem espaços ou aspas em volta do valor.

---

## Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|---|---|---|
| `OPENAI_API_KEY` | Sim | Chave da API Groq |
| `EMAIL_USER` | Sim | E-mail remetente e destinatário |
| `EMAIL_PASS` | Sim | Senha de app do Gmail |

---

## Licença

Uso interno. Todos os direitos reservados.
