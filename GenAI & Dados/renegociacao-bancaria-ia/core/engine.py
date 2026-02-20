import os
from groq import Groq

class AgenteNegociador:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key)
        self.model_id = "llama-3.3-70b-versatile"

    def responder(self, prompt_user, contexto_cliente, historico_formatado):
        system_msg = (
            "Você é o consultor RenovaIA. Seja direto, moderno e resolutivo."
            "\n- RESPOSTAS CURTAS: No máximo 3 frases."
            "\n- BOLETO: Use crases triplas: ```codigo```."
            "\n- FOCO: Fale de valores e abatimento de juros (BACEN) rapidamente."
            f"\n\nCONTEXTO: {contexto_cliente}"
        )

        messages = [{"role": "system", "content": system_msg}]
        messages.extend(historico_formatado)
        messages.append({"role": "user", "content": prompt_user})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            return completion.choices[0].message.content
        except:
            return "🤔 Tive um erro técnico. Pode repetir?"
