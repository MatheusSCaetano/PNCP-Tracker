from services.collect import get_editais
from services.parser import organize
from services.filter import filter
from services.storage import save, exists
from services.email_service import send_email
from services.collect_2 import coletar_licitacoes_reais, enriquecer_com_itens

def run():
    editais = coletar_licitacoes_reais()
    editais_com_itens = enriquecer_com_itens(editais)
    dados = organize(editais_com_itens)
    

    password = ["software juridico", "saas juridico", "recorte", "acompanhamento processos","DEDETIZAÇÃO", "Limpeza"]

    filtered = filter(dados,password )
    print(filtered)
    news = []

    for item in filtered:
        if not exists(item["id"]):
            save(item)
            news.append(item)

    send_email(filtered) #depois dos testes, trocar para news

if __name__ == "__main__":
    run()