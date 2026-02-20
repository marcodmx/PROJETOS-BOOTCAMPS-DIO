import os
from groq import Groq

class AgenteNegociador:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key)
        self.model_id = "llama-3.3-70b-versatile"

    def responder(self, prompt_user, contexto_cliente, historico_formatado):
        system_msg = (
            "Você é o Facilitador Estratégico do Banco RenovaIA S.A. "
            "Responda SEMPRE em texto direto, sem envolver em dicionários ou listas.\n\n"
            "DIRETRIZES:\n"
            "- NUNCA use: 'dívida', 'atraso' ou 'pendência'.\n"
            "- CET: 14.5% a.a. | Baixa: 3 dias úteis.\n"
            "- VALORES: Use SEMPRE <span style='font-size: 20px; color: #1e40af; font-weight: bold;'>R$ X.XXX,XX</span>.\n"
            "- BOLETO: Código SOZINHO em bloco de código (```).\n\n"
            f"CONTEXTO DO CLIENTE: {contexto_cliente}"
        )

        messages = [{"role": "system", "content": system_msg}]
        
        if historico_formatado:
            for msg in historico_formatado:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    # Garantimos que o conteúdo seja apenas a string de texto
                    content = msg["content"]
                    if isinstance(content, list): # Evita o erro de vir lista do Gradio
                        content = content[0] if content else ""
                    messages.append({"role": msg["role"], "content": str(content)})
        
        messages.append({"role": "user", "content": str(prompt_user)})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.3, # Aumentei um tiquinho para ela ser mais persuasiva
                max_tokens=800
            )
            resposta = completion.choices[0].message.content
            # Limpeza de segurança caso a IA tente retornar um dicionário como string
            if resposta.startswith("{'text'"):
                 import ast
                 try:
                     res_dict = ast.literal_eval(resposta)
                     return res_dict[0]['text'] if isinstance(res_dict, list) else res_dict['text']
                 except: pass
            return resposta
        except Exception as e:
            print(f"🚨 Erro Groq: {e}")
            return "⚠️ Tive um pequeno desencontro técnico. Pode repetir?"
