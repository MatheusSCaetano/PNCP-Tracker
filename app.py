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
    

    password = ["software juridico", "saas juridico", "recorte", "acompanhamento processos","DEDETIZAÇÃO"]

    filtrados = filter(dados,password )

    news = []

    for item in filtrados:
        if not exists(item["id"]):
            save(item)
            news.append(item)

    send_email(filtrados)

    print(f"Total coletado: {len(dados)}")
    #print("Exemplo de dado:")
    #print(dados[:100])

    print(f"Filtrados: {len(filtrados)}")
    #print("editais_com_itens",editais_com_itens)

if __name__ == "__main__":
    run()