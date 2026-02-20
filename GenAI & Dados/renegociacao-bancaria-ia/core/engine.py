import os
from groq import Groq

class AgenteNegociador:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key)
        self.model_id = "llama-3.3-70b-versatile"

    def responder(self, prompt_user, contexto_cliente, historico_formatado):
        system_msg = (
            "Você é o Facilitador Estratégico do Banco RenovaIA S.A. Seu tom é resolutivo, empático e profissional."
            "\n\nREGRAS DE OURO:"
            "\n1. NÃO REPITA informações que já estão no histórico recente (como valores ou códigos de boleto), a menos que o cliente peça explicitamente."
            "\n2. NEGOCIAÇÃO: Se o cliente propuser um valor abaixo da 'oferta_vista', diga que precisa de 30 segundos para consultar o 'Comitê de Crédito' (simule uma pausa dramática no texto)."
            "\n3. BOLETO: Quando solicitado, envie APENAS o código dentro de um bloco de código Markdown. Exemplo:"
            "\n```\n00000.00000 00000.000000 00000.000000 0 00000000000000\n```"
            "\n4. ESTILO: Use <span style='font-size: 20px; color: #1e40af; font-weight: bold;'>R$ X.XXX,XX</span> para valores."
            f"\n\nCONTEXTO ATUAL: {contexto_cliente}"
        )

        messages = [{"role": "system", "content": system_msg}]
        
        if historico_formatado:
            for msg in historico_formatado:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    # Limpeza de metadados para evitar Erro 400
                    clean_content = msg["content"][0] if isinstance(msg["content"], list) else msg["content"]
                    messages.append({"role": msg["role"], "content": str(clean_content)})
        
        messages.append({"role": "user", "content": str(prompt_user)})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.4, # Aumentado para respostas menos robóticas
                max_tokens=700
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"🚨 Erro Groq: {e}")
            return "⚠️ Tive um desencontro técnico. Pode repetir a última frase?"
