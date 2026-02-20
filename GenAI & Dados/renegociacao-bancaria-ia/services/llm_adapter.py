import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
Você é um assistente institucional de um grande banco.
Sua função é conduzir negociações de dívida com linguagem formal,
ética e profissional. Não ofereça condições fora das regras do sistema.
"""

def gerar_resposta(mensagem_usuario):
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": mensagem_usuario}
        ]
    )
    return completion.choices[0].message.content
