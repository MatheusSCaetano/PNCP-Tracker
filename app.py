from flask import app, jsonify, request, render_template
from flask import Flask
from services.parser import organize
from services.filter import filter
from services.storage import save, exists
from services.email_service import send_email
from services.collect import coletar_licitacoes_reais, enriquecer_com_itens

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/licitacoes", methods=["POST"])
def coletar_licitacoes():
    data = request.get_json()
    max_paginas = data.get("max_paginas", 5)
    tamanho = data.get("tamanho", 10)
    palavras_chave = data.get("palavras_chave")
    number_days = data.get("number_days", 7)

    # print("Dados recebidos:", data)

    editais = coletar_licitacoes_reais(max_paginas=max_paginas, tamanho=tamanho, palavras_chave=palavras_chave, number_days=number_days)
    # print(f"Editais coletados: {len(editais)}")
    # print("editais: ", editais)

    editais_com_itens = enriquecer_com_itens(editais)
    dados = organize(editais_com_itens)

    send_email(dados)
    return jsonify(dados)
    
if __name__ == "__main__":
    app.run(debug=True)