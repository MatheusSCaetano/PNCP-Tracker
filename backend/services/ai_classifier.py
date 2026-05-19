import os
import json 
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def classify_licitacao(text,prompt):
    prompt = f"""
        {prompt}

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