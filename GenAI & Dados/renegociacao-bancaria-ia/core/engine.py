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
            "\n\nREGRAS DE OURO:"
            "\n1. SEM TEXTÕES: Responda em no máximo 3 frases curtas."
            "\n2. DIRETO AO PONTO: Se o cliente quer oferta, diga os valores e o desconto à vista."
            "\n3. ABATIMENTO: Mencione o abatimento de juros (BACEN) de forma rápida."
            "\n4. BOLETO: Código sempre em bloco de notas: ```codigo```."
            "\n5. ESTILO: Use emojis, mas não seja 'forçado'. Tom de voz parceiro."
            f"\n\nCONTEXTO: {contexto_cliente}"
        )

        messages = [{"role": "system", "content": system_msg}]
        messages.extend(historico_formatado)
        messages.append({"role": "user", "content": prompt_user})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.3, # Mais focado
                max_tokens=500
            )
            return completion.choices[0].message.content
        except:
            return "🤔 Tive um erro técnico. Pode repetir?"
