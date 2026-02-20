import os
from groq import Groq

class AgenteNegociador:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key)
        self.model_id = "llama-3.3-70b-versatile"

    def responder(self, prompt_user, contexto_cliente, historico_formatado):
        system_msg = (
            "Você é o consultor RenovaIA. Direto e resolutivo."
            "\n\nREGRAS DE OURO:"
            "\n1. OFERTA MÍNIMA: Nunca sugira um valor superior à oferta à vista que está no contexto (R$ 1.850,00). Se o cliente pedir mais desconto, explique gentilmente que aquele já é o limite máximo permitido pelo sistema."
            "\n2. BOLETO: O código DEVE estar entre crases triplas em um bloco isolado. Exemplo:"
            "\n\n```"
            "\n00000.00000 00000.000000..."
            "\n```"
            "\n3. FORMATAÇÃO: Use obrigatoriamente: <span style='font-size: 20px; color: #1e40af; font-weight: bold;'>R$ X.XXX,XX</span> para valores."
            "\n4. CET: Sempre informe o CET do contexto."
            f"\n\nCONTEXTO DO CLIENTE: {contexto_cliente}"
        )

        messages = [{"role": "system", "content": system_msg}]
        messages.extend(historico_formatado)
        messages.append({"role": "user", "content": prompt_user})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.0, # Zero absoluto para evitar cálculos criativos errados
                max_tokens=400
            )
            return completion.choices[0].message.content
        except:
            return "🤔 Tive um erro técnico. Pode repetir?"
