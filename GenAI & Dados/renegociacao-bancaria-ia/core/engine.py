import os
from groq import Groq

class AgenteNegociador:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key)
        self.model_id = "llama-3.3-70b-versatile"

    def responder(self, prompt_user, contexto_cliente, historico_formatado):
        system_msg = (
            "Você é o Facilitador Estratégico do Banco RenovaIA S.A. Seu objetivo é ajudar na reorganização financeira."
            "\n\nREGRAS DE COMUNICAÇÃO:"
            "\n- NUNCA use: 'dívida', 'atraso', 'pendência' ou 'inadimplente'. Use: 'valor em aberto', 'oportunidade' ou 'ajuste'."
            "\n- FATOS REAIS: Use apenas os valores do contexto. O CET é de 14.5% a.a. e a baixa ocorre em até 3 dias úteis."
            "\n- NEGOCIAÇÃO: Se o cliente pedir desconto, tente manter a 'oferta_minima_avista'. Se ele insistir muito, diga que enviou para o 'Setor de Liberação' analisar."
            "\n\nFORMATAÇÃO OBRIGATÓRIA:"
            "\n- VALORES: <span style='font-size: 20px; color: #1e40af; font-weight: bold;'>R$ X.XXX,XX</span>."
            "\n- BOLETO: O código deve estar SOZINHO em um bloco de código (```) para o botão de cópia aparecer."
            f"\n\nCONTEXTO DO CLIENTE: {contexto_cliente}"
        )

        messages = [{"role": "system", "content": system_msg}]
        messages.extend(historico_formatado)
        messages.append({"role": "user", "content": prompt_user})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.1, # Evita alucinações
                max_tokens=600
            )
            return completion.choices[0].message.content
        except Exception:
            return "⚠️ Tive um desencontro técnico. Poderia repetir sua última frase?"
