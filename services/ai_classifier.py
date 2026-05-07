import os
import json 
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def classify_licitacao(text):
    prompt = f"""
        Você é um classificador de editais especializado em software jurídico.

        Sua tarefa:
        Determinar se o edital é relevante para uma empresa que desenvolve:

        - software jurídico
        - sistemas de gestão processual
        - plataformas SaaS jurídicas
        - automação jurídica
        - inteligência artificial jurídica
        - sistemas web jurídicos
        - integração com tribunais
        - acompanhamento processual

        Considere ALTAMENTE relevante quando mencionar:
        - software jurídico
        - SaaS
        - processos judiciais
        - gestão processual
        - IA jurídica
        - peças jurídicas
        - procuradoria
        - tribunais
        - workflow jurídico
        - plataforma web jurídica

        Responda SOMENTE JSON válido:

        {{
            "score": 0,
            "relevante": false,
            "motivo": "",
            "tecnologias": []
        }}

        REGRAS:
        - score >= 7 => relevante=true
        - score <= 6 => relevante=false

        Edital:
        {text}
    """
    response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1
        )

    content = response.choices[0].message.content

    try:
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except:
        return {
            "score": 0,
            "relevante": False,
            "motivo": "Erro ao interpretar resposta da IA",
            "tecnologias": [],
            "categoria": "desconhecido"
        }