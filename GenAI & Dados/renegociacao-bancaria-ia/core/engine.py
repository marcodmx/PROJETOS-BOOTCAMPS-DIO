import os
from groq import Groq

class AgenteNegociador:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key)
        self.model_id = "llama-3.3-70b-versatile"

    def responder(self, prompt_user, contexto_cliente, historico_formatado):
        system_msg = (
            "Você é o consultor RenovaIA. Direto, moderno e sem enrolação."
            "\n\nREGRAS CRÍTICAS:"
            "\n1. BOLETO: O código deve estar SOZINHO em um bloco de código Markdown para o botão de copiar aparecer. Exemplo:"
            "\n```"
            "\n000.000"
            "\n```"
            "\n2. BACEN: Não diga que o BACEN negocia ou abate. Diga apenas que o cliente tem 'direito ao abatimento proporcional de juros por antecipação'."
            "\n3. SEM LOROTA: Não explique cálculos de juros detalhados. Foque no valor final e na economia."
            "\n4. SUPORTE: Se o usuário pedir ajuda ou suporte, pergunte em que pode ajudar especificamente (dúvidas sobre boleto, prazos ou valores)."
            f"\n\nCONTEXTO: {contexto_cliente}"
        )

        messages = [{"role": "system", "content": system_msg}]
        messages.extend(historico_formatado)
        messages.append({"role": "user", "content": prompt_user})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.2, # Bem focado para evitar invenções
                max_tokens=400
            )
            return completion.choices[0].message.content
        except:
            return "🤔 Tive um erro técnico. Pode repetir?"
