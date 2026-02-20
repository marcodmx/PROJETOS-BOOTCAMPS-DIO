import os
from groq import Groq

class AgenteNegociador:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key)
        self.model_id = "llama-3.3-70b-versatile"

    def responder(self, prompt_user, contexto_cliente, historico_formatado):
        system_msg = (
            "Você é o consultor RenovaIA. Foco em ACESSIBILIDADE e CLAREZA."
            "\n\nREGRAS DE FORMATAÇÃO OBRIGATÓRIAS:"
            "\n1. VALORES: Sempre use R$ e formato brasileiro (ex: R$ 1.850,00). Use negrito: **R$ 1.850,00**."
            "\n2. BOLETO: Coloque o código sozinho em um bloco de código. ACIMA do bloco, escreva: <h3 style='color: #1e293b;'>CÓDIGO PARA COPIAR:</h3>"
            "\n3. CET: Informe sempre o CET (Custo Efetivo Total) que consta no contexto. Não invente números."
            "\n4. DESTAQUE VISUAL: Use a tag <h2> para valores principais de oferta para que fiquem grandes e legíveis."
            "\n5. DIRETO: Sem textos longos. Responda em até 3 frases."
            f"\n\nCONTEXTO: {contexto_cliente}"
        )

        messages = [{"role": "system", "content": system_msg}]
        messages.extend(historico_formatado)
        messages.append({"role": "user", "content": prompt_user})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.2,
                max_tokens=600
            )
            return completion.choices[0].message.content
        except:
            return "🤔 Tive um erro técnico. Pode repetir?"
