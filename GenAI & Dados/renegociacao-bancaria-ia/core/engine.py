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
            "\n\nREGRAS DE FORMATAÇÃO (ESTRITAS):"
            "\n1. VALORES: Use: <span style='font-size: 20px; color: #1e40af; font-weight: bold;'>R$ X.XXX,XX</span>."
            "\n2. BOLETO: Envie o código EXCLUSIVAMENTE dentro de um bloco de código Markdown puro, com uma linha vazia antes e depois. "
            "NUNCA use HTML dentro ou colado ao bloco de código. Exemplo:"
            "\n\n```"
            "\n00000.00000 00000.000000..."
            "\n```"
            "\n3. CONTEÚDO: Informe o CET e o direito ao abatimento proporcional de juros (normas BACEN) de forma breve."
            "\n4. ESTILO: Respostas em no máximo 3 frases curtas. Sem testões ou termos condescendentes."
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
