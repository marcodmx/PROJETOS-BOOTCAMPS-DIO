import os
from groq import Groq

class AgenteNegociador:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key)
        self.model_id = "llama-3.3-70b-versatile"

    def responder(self, prompt_user, contexto_cliente, historico_formatado):
        system_msg = (
            "Você é o consultor estratégico da RenovaIA. Seja direto, moderno e elegante."
            "\n\nREGRAS DE FORMATAÇÃO:"
            "\n1. VALORES: Destaque os valores em negrito e cor usando: <span style='font-size: 20px; color: #1e40af; font-weight: bold;'>R$ X.XXX,XX</span>"
            "\n2. BOLETO: O código deve estar SOZINHO em um bloco de código (```). Dê um 'Enter' antes e depois do bloco."
            "\n3. CET: Informe sempre o Custo Efetivo Total (CET) disponível no contexto."
            "\n4. ESTILO: Sem 'textões'. Responda em no máximo 3 frases. Seja cordial, mas resolutivo."
            "\n5. SUPORTE: Se o usuário pedir ajuda, pergunte como pode auxiliá-lo especificamente."
            f"\n\nCONTEXTO DO CLIENTE: {contexto_cliente}"
        )

        messages = [{"role": "system", "content": system_msg}]
        messages.extend(historico_formatado)
        messages.append({"role": "user", "content": prompt_user})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.1,
                max_tokens=500
            )
            return completion.choices[0].message.content
        except:
            return "🤔 Tive um pequeno problema técnico. Pode repetir?"
