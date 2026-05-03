# 📡 PNCP Monitor

Sistema automatizado para monitoramento de licitações públicas no PNCP, com filtragem inteligente e envio de notificações por e-mail.

---

## 🚀 Funcionalidades

* Coleta automática de licitações
* Enriquecimento com itens dos editais
* Filtro por palavras-chave
* Armazenamento de dados
* Notificação por e-mail
* Execução agendada (scheduler)

---

## 🛠️ Tecnologias

* Python
* APScheduler
* Integração com API do PNCP

---

## ⚙️ Como rodar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/pncp-monitor.git
cd pncp-monitor
```

### 2. Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```env
EMAIL_USER=seu_email
EMAIL_PASS=sua_senha
```

### 5. Executar o projeto

```bash
python app.py
```

Ou com agendamento:

```bash
python scheduler.py
```

---

## 📌 Observações

* O arquivo `.env` não é versionado por segurança
* O banco de dados local não é incluído no repositório

---

## 📬 Contato

Caso queira trocar ideia ou sugerir melhorias, fique à vontade!
