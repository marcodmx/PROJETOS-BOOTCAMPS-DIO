# core/engine.py
import os
from groq import Groq

class AgenteNegociador:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key)
        self.model_id = "llama-3.1-8b-instant"

    def responder(self, prompt_user, contexto_cliente, historico_formatado):
        system_msg = (
            "Você é um agente bancário institucional. Use apenas dados da base."
            " Se não souber algo, admita limitação e sugira contato com SAC."
        )
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": f"{contexto_cliente}. Pergunta: {prompt_user}"}
        ] + historico_formatado

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.2,
                max_tokens=1024
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Erro interno: {str(e)}"
