import os
import re
import ast
from groq import Groq

class AgenteNegociador:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key)
        self.model_id = "llama-3.3-70b-versatile"

    def responder(self, prompt_user, contexto_cliente, historico_formatado):
        system_msg = (
            "Você é o Facilitador Estratégico do Banco RenovaIA S.A. Responda APENAS com texto puro.\n"
            "NUNCA use dicionários ou chaves JSON na sua resposta.\n\n"
            "REGRAS:\n"
            "- VALORES: Use <span style=\"font-size: 20px; color: #1e40af; font-weight: bold;\">R$ X.XXX,XX</span>.\n"
            "- BOLETO: O código deve estar SOZINHO em um bloco de código (```).\n"
            "- Não repita informações que já estão no histórico.\n\n"
            f"CONTEXTO DO CLIENTE: {contexto_cliente}"
        )

        messages = [{"role": "system", "content": system_msg}]
        
        if historico_formatado:
            for msg in historico_formatado:
                if isinstance(msg, dict):
                    content = msg.get("content", "")
                    if isinstance(content, list): content = content[0] if content else ""
                    messages.append({"role": msg.get("role", "user"), "content": str(content)})
        
        messages.append({"role": "user", "content": str(prompt_user)})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.3
            )
            resposta = completion.choices[0].message.content

            # SANITIZAÇÃO ANTI-JSON
            if resposta.strip().startswith("{") or "text':" in resposta:
                try:
                    # Tenta converter string de dict em texto puro
                    res_dict = ast.literal_eval(resposta.strip())
                    if isinstance(res_dict, dict): return res_dict.get('text', resposta)
                    if isinstance(res_dict, list) and len(res_dict) > 0: return res_dict[0].get('text', resposta)
                except:
                    # Fallback via Regex para extrair o valor da chave 'text'
                    match = re.search(r"['\"]text['\"]:\s*['\"](.*?)['\"]", resposta, re.DOTALL)
                    if match: return match.group(1)

            return resposta
        except Exception as e:
            print(f"🚨 Erro Groq: {e}")
            return "⚠️ Tive um pequeno desencontro técnico. Pode repetir?"
