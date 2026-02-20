import os
from groq import Groq

class AgenteNegociador:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key)
        # Usando o modelo 70b para maior inteligência na negociação
        self.model_id = "llama-3.3-70b-versatile"

    def responder(self, prompt_user, contexto_cliente, historico_formatado):
        system_msg = (
            "Você é o consultor de saúde financeira da RenovaIA. "
            "Seu tom é empático, direto e acolhedor (como uma fintech moderna), mas transmitindo a segurança de uma instituição sólida."
            "\n\nDIRETRIZES:"
            "\n- Nunca envie textos gigantes. Vá por partes."
            "\n- Se o cliente aceitar uma oferta, gere o código do boleto e diga que enviou uma cópia por e-mail."
            "\n- Use emojis como 😊 e 🙌 para transmitir que 'vai dar tudo certo'."
            "\n- Se gerar um código de barras, coloque-o EXATAMENTE entre crases triplas para habilitar o botão de copiar no chat, assim:"
            "\n```\n23790.12345 60000.789012 34567.890123 1 95000000185000\n```"
            f"\n\nCONTEXTO DO CLIENTE: {contexto_cliente}"
        )

        messages = [{"role": "system", "content": system_msg}]
        messages.extend(historico_formatado)
        messages.append({"role": "user", "content": prompt_user})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.5,
                max_tokens=800
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"🤔 Tive um pequeno problema técnico, mas não desista! Pode repetir? (Erro: {str(e)})"
